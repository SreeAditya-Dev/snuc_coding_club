import requests
import json
import sys
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test a single API endpoint"""
    try:
        print(f"Testing {description}...")
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {description} - Success")
            
            # Print some details about the response
            if isinstance(data, list):
                print(f"  → Returned {len(data)} items")
            elif isinstance(data, dict):
                print(f"  → Returned object with {len(data)} keys")
            
            return True
        else:
            print(f"✗ {description} - Failed (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ {description} - Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("=" * 50)
    print("Best Club Award System - API Test")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # List of endpoints to test
    endpoints = [
        ("/", "Health Check"),
        ("/clubs", "Get All Clubs"),
        ("/clubs/1", "Get Club by ID"),
        ("/groups", "Get Club Groups"),
        ("/rankings/overall", "Get Overall Rankings"),
        ("/analytics/social-media/1", "Get Social Media Analytics"),
        ("/analytics/events/1", "Get Event Analytics"),
        ("/analytics/whatsapp/1", "Get WhatsApp Analytics"),
        ("/voting/summary", "Get Voting Summary"),
        ("/dashboard/stats", "Get Dashboard Stats"),
    ]
    
    # Run tests
    passed = 0
    total = len(endpoints)
    
    for endpoint, description in endpoints:
        if test_endpoint(endpoint, description):
            passed += 1
        print()  # Empty line for readability
    
    # Summary
    print("-" * 50)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the backend server.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
