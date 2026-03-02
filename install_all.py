"""
Install all required packages for LinguaAsset-QA
"""

import subprocess
import sys

packages = [
    "langchain",
    "langchain-community",
    "langchain-google-genai",
    "langchain-chroma",
    "chromadb",
    "sentence-transformers",
    "pandas",
    "python-docx",
    "python-dotenv",
    "langdetect",
    "googletrans==4.0.0rc1",
    "streamlit",
    "tabulate",
    "unstructured",
    "tqdm",
    "colorlog"
]

print("📦 Installing all required packages...")
print("="*50)

for package in packages:
    print(f"\n🔄 Installing: {package}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed: {package}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install: {package}")
        print(f"   Error: {e}")

print("\n" + "="*50)
print("🎉 All installations attempted!")
print("\n🔍 Verifying installations...")

# Test imports
test_modules = [
    "langchain",
    "langchain_community",
    "langchain_google_genai",
    "langchain_chroma",
    "chromadb",
    "pandas",
]

print("\n📋 Verification Results:")
for module in test_modules:
    try:
        __import__(module.replace("-", "_"))
        print(f"✅ {module:25} - OK")
    except ImportError as e:
        print(f"❌ {module:25} - Failed: {e}")

print("\n" + "="*50)