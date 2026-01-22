#!/usr/bin/env python3
"""Test what's available in installed masumi package"""
import sys

print("Python version:", sys.version)
print("\nTesting masumi imports...")

try:
    import masumi
    print(f"✅ masumi version: {masumi.__version__}")
    print(f"\nAvailable in masumi:")
    exports = [x for x in dir(masumi) if not x.startswith('_')]
    for exp in exports:
        print(f"  - {exp}")
    
    # Test specific imports
    print("\n=== Testing key imports ===")
    
    try:
        from masumi import run
        print("✅ masumi.run is available")
    except ImportError as e:
        print(f"❌ masumi.run NOT available: {e}")
    
    try:
        from masumi import MasumiAgentServer, Config
        print("✅ MasumiAgentServer and Config available")
    except ImportError as e:
        print(f"❌ MasumiAgentServer/Config NOT available: {e}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
