#!/usr/bin/env python3
"""Quick diagnostic for WP4 dependencies"""

import sys
print("Python Version:", sys.version)

# Test basic imports
try:
    import re
    print("✅ re module available")
except ImportError as e:
    print("❌ re module missing:", e)

try:
    from typing import Dict, List, Optional
    print("✅ typing module available")
except ImportError as e:
    print("❌ typing module missing:", e)

# Test spaCy
try:
    import spacy
    print(f"✅ spaCy installed: {spacy.__version__}")
    try:
        nlp = spacy.load('en_core_web_sm')
        print("✅ spaCy model loaded successfully")
    except OSError:
        print("⚠️  spaCy model not found. Installing...")
        import subprocess
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=False)
except ImportError:
    print("❌ spaCy not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "spacy", "-q"], check=False)

print("\n✅ Dependency check complete")
