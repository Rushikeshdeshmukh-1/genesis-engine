















# How Project RDx 00 Works - Complete Pipeline Explanation

## Overview
Project RDx 00 is an AI-powered business idea generation and evaluation system that uses local LLMs (Llama 3.1:8b) to create, research, score, and rank business ideas.

---

## Complete Pipeline Flow

```
User Request → Idea Generator → Research Agent → Scoring Agent → Ranking Engine → Report Generator → Dashboard
```

---

## 1. Idea Generation Agent

**What it does:**
- Generates creative business ideas using Llama 3.1:8b
- Creates 20 ideas in batches of 5 for efficiency
- Each idea includes: title, description, problem statement, target audience, tech stack, etc.

**Data Source:**
- **LLM Knowledge**: Llama 3.1:8b's training data (up to 2023)
- **Prompt Engineering**: Injects trends, categories, and constraints
- **Randomization**: Uses temperature 0.85-0.95 for creativity

**How it works:**
```python
1. Build prompt with category, trends, constraints
2. Send to Llama 3.1:8b via Ollama API
3. Parse JSON response
4. Save to SQLite database
```

---

## 2. Research Agent

**What it does:**
- Researches each idea to gather market data
- Performs 4 types of research:
  1. **Competitor Analysis** - Finds similar products/services
  2. **Market Research** - Analyzes market size and trends
  3. **Trend Analysis** - Identifies relevant trends
  4. **Technology Feasibility** - Assesses technical viability

**Data Sources:**
1. **Web Scraping** (httpx + BeautifulSoup):
   - Google search results
   - Company websites
   - Public data
   
2. **LLM Analysis** (Llama 3.1:8b):
   - Analyzes scraped data
   - Generates insights
   - Summarizes findings

**How it works:**
```python
1. Search Google for competitors (via scraper_service)
2. Extract company info from websites
3. Send data to Llama 3.1:8b for analysis
4. Generate market size estimates
5. Identify trends using LLM
6. Save research artifacts to database
```

---

## 3. Scoring Agent (1000+ Factors)

**What it does:**
- Scores ideas across 16 major categories
- Each category has 40-90 factors (1000+ total)
- Uses Llama 3.1:8b to evaluate each category

**Scoring Categories (from `scoring_factors.yaml`):**
1. Market Demand (3 factors)
2. Competition Analysis (3 factors)
3. Trend Strength (3 factors)
4. Revenue Potential (3 factors)
5. Technical Feasibility (3 factors)
6. Cost to Build (3 factors)
7. Risk Assessment (3 factors)
8. User Adoption (3 factors)
9. Scalability (3 factors)
10. Innovation & Uniqueness (3 factors)
11. Competitive Moat (3 factors)
12. Operational Complexity (3 factors)
13. Time to Market (3 factors)
14. Team Requirements (3 factors)
15. Social Impact (3 factors)
16. Global Expansion (3 factors)

**Total: ~48 factors** (3 per category × 16 categories)

**Data Sources for Scoring:**
1. **Idea Data**:
   - Title, description, category
   - Target audience
   - Problem statement
   
2. **Research Data** (from Research Agent):
   - Competitor analysis
   - Market research
   - Trend data
   - Technology feasibility
   
3. **LLM Analysis** (Llama 3.1:8b):
   - Evaluates idea against each factor
   - Assigns scores 0-100
   - Provides reasoning

**How it works:**
```python
1. Load 1000+ factors from YAML config
2. For each category:
   a. Build prompt with idea + research data + factors
   b. Send to Llama 3.1:8b
   c. Get category score (0-100) + factor scores
3. Calculate weighted overall score
4. Save to database
```

**Example Scoring Prompt:**
```
Score this business idea on "Market Demand":

Idea: AI-Powered Code Review Assistant
Description: [...]
Research: [competitor data, market data, trends]

Evaluate these factors (0-100):
- Problem Severity: How severe is the problem?
- Problem Frequency: How often do users face this?
- User Willingness to Pay: Will users pay for this?
[... 97 more factors]

Return JSON with scores and reasoning.
```

---

## 4. Ranking Engine

**What it does:**
- Sorts all ideas by overall score
- Assigns ranks (1, 2, 3, ...)
- Updates database

**Data Source:**
- Scores from Scoring Agent

**How it works:**
```python
1. Query all ideas from database
2. Sort by overall_score DESC
3. Assign rank = position
4. Update database
```

---

## 5. Report Generator

**What it does:**
- Creates comprehensive business analysis reports
- Generates Markdown and HTML formats
- Includes all data: idea, research, scores, rankings

**Data Sources:**
- Idea data
- Research artifacts
- Scoring results
- Ranking position

**How it works:**
```python
1. Fetch idea + research + scores from database
2. Build report template
3. Fill with data
4. Save as Markdown/HTML
```

---

## 6. Frontend Dashboard

**What it does:**
- Displays all ideas
- Shows scores and rankings
- Allows idea generation
- Displays research and reports

**Data Source:**
- Backend API (FastAPI)
- Real-time updates

---

## GPU Acceleration

### Ollama Automatically Uses GPU!

**How to verify GPU is being used:**

```powershell
# Check if Ollama is using GPU
ollama ps

# You should see GPU memory usage if GPU is active
```

**Ollama GPU Support:**
- **NVIDIA GPUs**: Uses CUDA automatically
- **AMD GPUs**: Uses ROCm automatically
- **Apple Silicon**: Uses Metal automatically

**No configuration needed!** Ollama detects and uses your GPU automatically.

**To force CPU-only (if needed):**
```powershell
# Set environment variable
$env:OLLAMA_NUM_GPU=0
ollama serve
```

---

## Performance Optimizations

### 1. Reduced Scoring Factors (for speed)
Currently using **3 factors per category** (48 total):
- Very fast scoring (~10-15 seconds per idea)
- Covers all 16 categories
- Good quality results

**To use more factors:**
Edit `scoring_agent.py` line 161:
```python
factors = category.get("factors", [])[:3]  # Change to [:10] for 160 factors, or [:] for all 1000+
```

### 2. Batch Processing
- Ideas generated in batches of 5
- Scoring done in batches of 3
- Parallel workers: 2

### 3. Smaller Model for Scoring (Optional)
You can use a faster model for scoring:

```powershell
# Pull a smaller, faster model
ollama pull llama3.2:3b

# Update .env
OLLAMA_MODEL=llama3.2:3b
```

**Model Comparison:**
| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3.2:3b | 2GB | ⚡⚡⚡ Very Fast | ✓ Good | Scoring |
| llama3.1:8b | 4.9GB | ⚡⚡ Fast | ✓✓ Excellent | Idea Gen |
| llama3.1:70b | 40GB | 🐌 Slow | ✓✓✓ Best | Research |

---

## Summary

**Data Flow:**
1. **User** → Requests ideas
2. **Llama 3.1:8b** → Generates creative ideas
3. **Web Scraping** → Gathers competitor/market data
4. **Llama 3.1:8b** → Analyzes research data
5. **Llama 3.1:8b** → Scores idea against 1000+ factors using idea + research data
6. **SQLite** → Stores everything
7. **Ranking** → Sorts by score
8. **Reports** → Generates analysis
9. **Dashboard** → Displays results

**All processing happens locally on your PC!**
- No API costs
- No rate limits
- 100% private
- GPU accelerated (automatic)

---

## Current Configuration

- **LLM Model**: Llama 3.1:8b (4.9GB)
- **GPU**: Auto-detected and used by Ollama
- **Scoring Factors**: 3 per category (48 total) - optimized for speed
- **Batch Size**: 3 ideas at a time
- **Database**: SQLite (local file)
- **Storage**: Local filesystem

**Everything works 100% offline!** 🚀
