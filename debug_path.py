"""
Debug path issues in your project
"""

import os
from pathlib import Path
import config

print("🔍 PATH DEBUG INFORMATION")
print("="*50)

# Current working directory
print(f"Current working directory: {Path.cwd()}")

# Check config
print(f"\nConfig settings:")
print(f"TRAINING_DATA_DIR = {config.TRAINING_DATA_DIR}")
print(f"DB_DIRECTORY = {config.DB_DIRECTORY}")

# Build full path
training_path = Path(config.TRAINING_DATA_DIR)
print(f"\nFull training path: {training_path.absolute()}")

# Check if directory exists
print(f"Directory exists: {training_path.exists()}")

# List files if directory exists
if training_path.exists():
    files = list(training_path.glob('*'))
    print(f"\nFiles in directory ({len(files)}):")
    for f in files:
        print(f"  - {f.name} ({f.suffix})")
else:
    print(f"\n❌ Directory does not exist! Creating it...")
    training_path.mkdir(exist_ok=True)
    print(f"✅ Created directory: {training_path.absolute()}")

print("\n" + "="*50)