"""
LLM Service for interacting with Google Gemini API.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM interactions using Google Gemini."""
    
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.timeout = settings.gemini_timeout
        
    def _get_model(self, temperature: float = 0.7, json_mode: bool = False):
        """Get configured Gemini model instance."""
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
        
        return genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config
        )
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            json_mode: Whether to force JSON output
            
        Returns:
            Generated text
        """
        try:
            model = self._get_model(temperature=temperature, json_mode=json_mode)
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Generate content
            response = model.generate_content(full_prompt)
            
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Chat completion using Gemini API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            json_mode: Whether to force JSON output
            
        Returns:
            Generated response
        """
        try:
            model = self._get_model(temperature=temperature, json_mode=json_mode)
            
            # Convert messages to Gemini format
            chat = model.start_chat(history=[])
            
            # Process messages
            system_message = None
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "system":
                    system_message = content
                elif role == "user":
                    # Prepend system message to first user message if exists
                    if system_message:
                        content = f"{system_message}\n\n{content}"
                        system_message = None
                    
                    response = chat.send_message(content)
                elif role == "assistant":
                    # Add assistant message to history (Gemini handles this automatically)
                    pass
            
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API chat failed: {e}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate JSON output from Gemini API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON response
        """
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            json_mode=True
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Gemini API is available."""
        try:
            # Try a simple generation to check API availability
            model = self._get_model(temperature=0.1)
            response = model.generate_content("Say 'OK'")
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini API health check failed: {e}")
            return False
