"""
Debug test to see what's going wrong
"""

import os
import sys
from pathlib import Path

print("="*50)
print("🔍 DEBUG INFORMATION")
print("="*50)

# Check Python version
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# Check current directory
current_dir = Path.cwd()
print(f"Current directory: {current_dir}")
print(f"Files in directory: {[f.name for f in current_dir.glob('*')]}")
print()

# Check .env file
env_path = current_dir / '.env'
if env_path.exists():
    print(f"✅ .env file exists at: {env_path}")
    print(f"File size: {env_path.stat().st_size} bytes")
    
    # Read first few characters safely
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'OPENROUTER_API_KEY=' in content:
            key_start = content.find('OPENROUTER_API_KEY=') + 19
            key = content[key_start:].strip()
            print(f"✅ API key format looks correct (starts with: {key[:10]}...)")
        else:
            print("❌ OPENROUTER_API_KEY not found in .env")
else:
    print("❌ .env file not found!")
print()

# Try to load with dotenv
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv imported successfully")
    
    result = load_dotenv()
    print(f"load_dotenv() returned: {result}")
    
    # Check if key is now in environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        print(f"✅ API key loaded from environment: {api_key[:10]}...")
    else:
        print("❌ API key NOT found in environment after load_dotenv()")
        
except ImportError as e:
    print(f"❌ Failed to import dotenv: {e}")
except Exception as e:
    print(f"❌ Error loading dotenv: {e}")
print()

# Test direct file reading
print("Testing direct file read:")
try:
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"File has {len(lines)} lines")
        for i, line in enumerate(lines):
            print(f"  Line {i+1}: {line.strip()}")
except Exception as e:
    print(f"❌ Failed to read .env: {e}")
print()

# Try to set environment variable manually
print("Setting environment variable manually:")
os.environ['OPENROUTER_API_KEY'] = content.split('=')[1].strip()
print(f"✅ Manually set: {os.environ['OPENROUTER_API_KEY'][:10]}...")
print()

# Test OpenRouter connection
print("Testing OpenRouter connection:")
try:
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model="qwen/qwen3-4b:free",
        openai_api_key=os.environ['OPENROUTER_API_KEY'],
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=50,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "LinguaAsset-QA Debug"
        }
    )
    
    response = llm.invoke("Say 'Hello' in one word")
    print(f"✅ OpenRouter connection successful!")
    print(f"Response: {response.content}")
    
except Exception as e:
    print(f"❌ OpenRouter connection failed: {e}")

print("="*50)