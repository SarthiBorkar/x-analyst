#!/usr/bin/env python3
"""
Test script to verify the /input_schema endpoint is working correctly
"""
import requests
import json
import sys

def test_input_schema(base_url="http://localhost:8080"):
    """Test the /input_schema endpoint"""
    url = f"{base_url}/input_schema"
    
    print("=" * 60)
    print("Testing /input_schema Endpoint")
    print("=" * 60)
    print(f"\nURL: {url}\n")
    
    try:
        response = requests.get(url, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ Success! Response:")
                print(json.dumps(data, indent=2))
                
                # Validate structure
                if "input_data" in data:
                    print(f"\n✅ Schema has 'input_data' field with {len(data['input_data'])} fields")
                    for field in data['input_data']:
                        required_fields = ['id', 'type', 'name']
                        missing = [f for f in required_fields if f not in field]
                        if missing:
                            print(f"  ⚠️  Field '{field.get('id', 'unknown')}' missing: {missing}")
                        else:
                            print(f"  ✅ Field '{field['id']}' looks valid")
                else:
                    print(f"\n❌ Schema missing 'input_data' field")
                    print(f"   Available keys: {list(data.keys())}")
                
            except json.JSONDecodeError as e:
                print(f"\n❌ Response is not valid JSON: {e}")
                print(f"   Response text: {response.text[:200]}")
        else:
            print(f"\n❌ Error response:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Could not connect to {url}")
        print(f"   Make sure your agent server is running!")
        print(f"   Try: python main.py")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout: Request took too long")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    return response.status_code == 200

if __name__ == "__main__":
    # Allow custom URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    success = test_input_schema(base_url)
    sys.exit(0 if success else 1)
