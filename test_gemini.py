"""
Test Google Gemini connection
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("❌ ERROR: No GOOGLE_API_KEY found in .env file")
    print("Please add: GOOGLE_API_KEY=your-gemini-api-key")
    exit(1)

print(f"✅ API Key loaded: {api_key[:10]}...")

# Test different models
models = [
    "gemini-3-flash",
    "gemini-2.5-flash",
    "gemma-3-27b-it",
    "gemma-3-12b-it"
]

for model in models:
    print(f"\n🤖 Testing model: {model}")
    try:
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.7,
            max_tokens=100,
            convert_system_message_to_human=True
        )
        
        response = llm.invoke("Say 'Hello' in 3 languages (English, Hindi, Spanish)")
        print(f"✅ Success: {response.content}")
        print(f"✅ {model} is working!")
        
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}...")

print("\n🎉 Testing complete!")