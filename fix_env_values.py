#!/usr/bin/env python3
"""
Helper script to fix environment variable formats
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Environment Variable Fix Helper")
print("=" * 60)

# Check AGENT_IDENTIFIER
agent_id = os.getenv("AGENT_IDENTIFIER", "")
print(f"\n1. AGENT_IDENTIFIER:")
print(f"   Current length: {len(agent_id)} characters")
print(f"   Current value: {agent_id}")

if len(agent_id) > 56:
    print(f"\n   ⚠️  Your AGENT_IDENTIFIER is {len(agent_id)} characters, but needs exactly 56.")
    print(f"   💡 Possible solutions:")
    print(f"      - If it's a URL, extract just the identifier part")
    print(f"      - If it has extra text, use only the first 56 characters")
    print(f"      - Check the admin interface for the correct 56-character identifier")
    
    # Try to find a 56-character substring
    if len(agent_id) >= 56:
        # Check if there's a 56-char hex string in it
        import re
        hex_pattern = r'[a-f0-9]{56}'
        matches = re.findall(hex_pattern, agent_id.lower())
        if matches:
            print(f"\n   ✅ Found potential 56-character hex identifier: {matches[0]}")
            print(f"   💡 Try using this value in your .env file")
        else:
            # Just take first 56 chars
            suggested = agent_id[:56]
            print(f"\n   💡 Suggested (first 56 chars): {suggested}")
            print(f"   ⚠️  Verify this is correct in the admin interface!")

# Check SELLER_VKEY
seller_vkey = os.getenv("SELLER_VKEY", "")
print(f"\n2. SELLER_VKEY:")
print(f"   Current length: {len(seller_vkey)} characters")
print(f"   Current value: {seller_vkey[:20]}...{seller_vkey[-10:] if len(seller_vkey) > 30 else seller_vkey}")

if len(seller_vkey) != 64:
    print(f"\n   ⚠️  Your SELLER_VKEY is {len(seller_vkey)} characters, but needs exactly 64 hex characters.")
    print(f"   💡 Solutions:")
    
    if len(seller_vkey) < 64:
        print(f"      - Your key is incomplete (missing {64 - len(seller_vkey)} characters)")
        print(f"      - Go back to the admin interface and copy the FULL 64-character key")
        print(f"      - Make sure you copied the entire key, not a truncated version")
        print(f"      - Check if the key is split across multiple lines in the admin interface")
    
    if len(seller_vkey) > 64:
        print(f"      - Your key has extra characters")
        print(f"      - Extract just the 64-character hex part")
    
    print(f"\n   📋 What to look for in admin interface:")
    print(f"      - Wallet section → Verification Key")
    print(f"      - Payment Sources section → Seller VKey")
    print(f"      - Should be exactly 64 hex characters (0-9, a-f)")
    print(f"      - Format examples:")
    print(f"        * Raw: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456")
    print(f"        * Prefixed: ed25519_a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456")

print("\n" + "=" * 60)
print("Next Steps:")
print("1. Go to Masumi admin interface")
print("2. For AGENT_IDENTIFIER: Copy the exact 56-character identifier")
print("3. For SELLER_VKEY: Copy the complete 64-character hex key")
print("4. Update your .env file with the correct values")
print("5. Run: python3 check_env_values.py to verify")
print("=" * 60)
