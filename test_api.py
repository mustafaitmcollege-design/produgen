"""
ProduGen - API Test Script
Tests the core API endpoints locally.
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 50)
    print("🧪 ProduGen API End-to-End Test")
    print("=" * 50)

    # 1. Health Check
    try:
        res = requests.get(f"{BASE_URL}/api/health")
        res.raise_for_status()
        data = res.json()
        print("✅ Health Check Passed!")
        print(f"   API Keys Status: {json.dumps(data['api_keys'])}")
    except Exception as e:
        print("❌ Health Check Failed. Is the server running (python run.py)?")
        print(f"   Error: {e}")
        return

    # 2. Check Sessions List
    try:
        res = requests.get(f"{BASE_URL}/api/sessions")
        res.raise_for_status()
        data = res.json()
        print(f"✅ Sessions List Passed! ({len(data['sessions'])} sessions found)")
    except Exception as e:
        print("❌ Sessions List Failed.")
        print(f"   Error: {e}")
        return

    print("\n✅ All basic API tests passed! Please use the web interface at http://localhost:8000 for full end-to-end testing with image upload and generation.")

if __name__ == "__main__":
    test_api()
