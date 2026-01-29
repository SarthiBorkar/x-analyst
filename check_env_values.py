#!/usr/bin/env python3
"""
Quick script to check AGENT_IDENTIFIER and SELLER_VKEY format
"""
import os
import re
from dotenv import load_dotenv

load_dotenv()

def is_hex_string(value: str) -> bool:
    """Check if a string is a valid hexadecimal string."""
    try:
        int(value, 16)
        return True
    except ValueError:
        return False

print("=" * 60)
print("Checking Environment Variable Formats")
print("=" * 60)

# Check AGENT_IDENTIFIER
agent_id = os.getenv("AGENT_IDENTIFIER", "")
print(f"\nAGENT_IDENTIFIER:")
print(f"  Length: {len(agent_id)} characters")
print(f"  Value: {agent_id[:20]}...{agent_id[-20:] if len(agent_id) > 40 else agent_id}")
if len(agent_id) != 56:
    print(f"  ❌ ERROR: Must be exactly 56 characters (got {len(agent_id)})")
    if len(agent_id) > 56:
        print(f"  💡 TIP: You might have copied extra text. Try using only the first 56 characters.")
        print(f"  💡 Or check if you copied a URL instead of just the identifier.")
else:
    if re.match(r'^[a-zA-Z0-9_-]+$', agent_id):
        print(f"  ✅ Format looks valid!")
    else:
        print(f"  ❌ Contains invalid characters (only alphanumeric, hyphens, underscores allowed)")

# Check SELLER_VKEY
seller_vkey = os.getenv("SELLER_VKEY", "")
print(f"\nSELLER_VKEY:")
print(f"  Length: {len(seller_vkey)} characters")
print(f"  Value: {seller_vkey[:20]}...{seller_vkey[-20:] if len(seller_vkey) > 40 else seller_vkey}")

if not seller_vkey:
    print(f"  ❌ ERROR: SELLER_VKEY is empty")
else:
    seller_vkey = seller_vkey.strip()
    
    # Check if prefixed format
    if '_' in seller_vkey:
        parts = seller_vkey.split('_', 1)
        if len(parts) == 2:
            prefix, key_part = parts
            print(f"  Format: Prefixed (prefix: '{prefix}')")
            print(f"  Key part length: {len(key_part)} characters")
            if is_hex_string(key_part):
                if len(key_part) == 64:
                    print(f"  ✅ Format is valid! (64 hex characters)")
                else:
                    print(f"  ❌ ERROR: Hex part must be exactly 64 characters (got {len(key_part)})")
            else:
                print(f"  ❌ ERROR: Key part is not valid hex")
                print(f"  💡 TIP: Hex strings can only contain: 0-9, a-f, A-F")
                print(f"  💡 Check for spaces, newlines, or invalid characters")
        else:
            print(f"  ❌ ERROR: Invalid prefixed format")
    # Check if raw hex
    elif is_hex_string(seller_vkey):
        print(f"  Format: Raw hex string")
        if len(seller_vkey) == 64:
            print(f"  ✅ Format is valid! (64 hex characters)")
        else:
            print(f"  ❌ ERROR: Must be exactly 64 hex characters (got {len(seller_vkey)})")
    # Check if Base58 (Cardano address)
    elif 58 <= len(seller_vkey) <= 103:
        if re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', seller_vkey):
            print(f"  ✅ Format looks like valid Base58 Cardano address!")
        else:
            print(f"  ❌ ERROR: Invalid Base58 format")
    else:
        print(f"  ❌ ERROR: Invalid format")
        print(f"  💡 Expected formats:")
        print(f"     - 64 hex characters (raw): 'a1b2c3d4...'")
        print(f"     - Prefixed: 'ed25519_a1b2c3d4...' (64 hex chars after _)")
        print(f"     - Base58 address: 58-103 characters")

print("\n" + "=" * 60)
print("💡 TIP: Make sure there are no extra spaces, newlines, or quotes")
print("   in your .env file values!")
print("=" * 60)
