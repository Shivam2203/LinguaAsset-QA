"""
Quick test for OpenRouter connection
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('OPENROUTER_API_KEY')

if not api_key:
    print("❌ ERROR: No OPENROUTER_API_KEY found in .env file")
    print("Please add: OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx")
    exit(1)

print(f"✅ API Key loaded: {api_key[:10]}...")

# Test different models
models = [
    "qwen/qwen3-4b:free",
    "openai/gpt-oss-120b:free",
    "meta-llama/llama-3.3-70b-instruct:free"
]

for model in models:
    print(f"\n🤖 Testing model: {model}")
    try:
        llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
            max_tokens=100,
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "LinguaAsset-QA Test"
            }
        )
        
        response = llm.invoke("Say 'Hello, LinguaAsset-QA is working!' in 3 languages")
        print(f"✅ Success: {response.content}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")

print("\n🎉 Testing complete!")