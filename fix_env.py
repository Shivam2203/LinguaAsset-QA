"""
Fix .env file encoding
"""

# Your API key
api_key = "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"

# Write with correct UTF-8 encoding (no BOM)
with open('.env', 'w', encoding='utf-8') as f:
    f.write(f"OPENROUTER_API_KEY={api_key}\n")

print("✅ .env file recreated with correct UTF-8 encoding")

# Verify it's readable
with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()
    print(f"File content: {content.strip()}")
    print(f"✅ File is readable!")