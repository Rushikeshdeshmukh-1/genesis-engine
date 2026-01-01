"""
Simplified web scraper service using httpx and BeautifulSoup.
Replaces Playwright for simpler, lighter web scraping.
"""

import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)


class ScraperService:
    """Simple web scraper using httpx and BeautifulSoup."""
    
    def __init__(self):
        self.client = None
        self.max_retries = settings.scraper_max_retries
        self.rate_limit_delay = settings.scraper_rate_limit_delay
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def search_google(
        self,
        query: str,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Google and return REAL results by scraping Google search page.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, url, snippet
        """
        logger.info(f"Searching Google for: {query}")
        
        # Try real Google scraping first
        try:
            results = await self._scrape_google_search(query, num_results)
            if results:
                logger.info(f"Successfully scraped {len(results)} real results from Google")
                return results
        except Exception as e:
            logger.warning(f"Google scraping failed: {e}")
        
        # Fallback to SerpAPI if configured
        if settings.serpapi_api_key and settings.serpapi_api_key != "your_serpapi_key_here":
            return await self._search_with_serpapi(query, num_results)
        
        # Last resort: mock results
        logger.warning("Using mock search results - real scraping failed")
        return self._get_mock_search_results(query, num_results)
    
    async def _scrape_google_search(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape Google search results directly (no API needed).
        """
        try:
            # Build Google search URL
            encoded_query = quote_plus(query)
            url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
            
            # Fetch Google search page
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            # Find search result divs (Google's structure)
            search_divs = soup.find_all('div', class_='g')
            
            for div in search_divs[:num_results]:
                try:
                    # Extract title and URL
                    title_elem = div.find('h3')
                    link_elem = div.find('a')
                    snippet_elem = div.find('div', class_=['VwiC3b', 'yXK7lf'])
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text()
                        url = link_elem.get('href', '')
                        snippet = snippet_elem.get_text() if snippet_elem else ""
                        
                        # Clean URL (remove Google tracking)
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        if url and url.startswith('http'):
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "source": "google_scrape"
                            })
                except Exception as e:
                    logger.debug(f"Failed to parse search result: {e}")
                    continue
            
            return results
        
        except Exception as e:
            logger.error(f"Google scraping error: {e}")
            return []
    
    async def _search_with_serpapi(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """Search using SerpAPI."""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": settings.serpapi_api_key,
                "num": num_results
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "snippet": item.get("snippet", "")
                })
            
            return results
        
        except Exception as e:
            logger.error(f"SerpAPI search failed: {e}")
            return self._get_mock_search_results(query, num_results)
    
    def _get_mock_search_results(
        self,
        query: str,
        num_results: int
    ) -> List[Dict[str, Any]]:
        """Return mock search results for testing."""
        results = []
        for i in range(min(num_results, 3)):
            results.append({
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"This is a mock search result for testing purposes. Query: {query}"
            })
        return results
    
    async def extract_company_info(self, url: str) -> Dict[str, Any]:
        """
        Extract basic company information from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with extracted information
        """
        try:
            logger.info(f"Extracting info from: {url}")
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            info = {
                "title": soup.title.string if soup.title else "Unknown",
                "description": self._extract_meta_description(soup),
                "url": url
            }
            
            return info
        
        except Exception as e:
            logger.warning(f"Failed to extract info from {url}: {e}")
            return {"url": url, "error": str(e)}
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from HTML."""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            return meta_desc.get("content")
        
        # Try og:description
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc and og_desc.get("content"):
            return og_desc.get("content")
        
        return "No description available"
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a web page and return HTML content.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                
                # Rate limiting
                if attempt > 0:
                    await asyncio.sleep(self.rate_limit_delay)
                
                return response.text
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.rate_limit_delay)
        
        return None
