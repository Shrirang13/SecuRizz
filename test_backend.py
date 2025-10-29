#!/usr/bin/env python3
import requests
import time

def test_backend():
    print("Testing backend...")
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is running!")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not responding: {e}")
        return False
    
    try:
        # Test analyze endpoint
        test_data = {
            "source_code": "// Test contract\ncontract Test {}",
            "contract_name": "Test"
        }
        response = requests.post('http://localhost:8000/analyze', json=test_data, timeout=10)
        print(f"Analyze endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ Analysis endpoint working!")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Analysis endpoint failed: {e}")
        return False

if __name__ == "__main__":
    test_backend()
