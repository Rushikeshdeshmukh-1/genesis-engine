"""
List all available Gemini models and their supported methods.
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("="*80)
print("AVAILABLE GEMINI MODELS")
print("="*80)

# List all models
models = genai.list_models()

print("\nModels that support 'generateContent':\n")
for model in models:
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description}")
        print(f"   Supported Methods: {', '.join(model.supported_generation_methods)}")
        print()

print("\n" + "="*80)
print("All available models:")
print("="*80)
for model in models:
    print(f"- {model.name}")
    print(f"  Methods: {', '.join(model.supported_generation_methods)}")
    print()
