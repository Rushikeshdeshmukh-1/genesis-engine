import asyncio
import logging
import sys
import os
import google.generativeai as genai

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_models():
    print("Listing available models with API Key:", settings.gemini_api_key[:10] + "...")
    genai.configure(api_key=settings.gemini_api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
