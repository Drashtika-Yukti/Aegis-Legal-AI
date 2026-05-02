import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_security_breach():
    print("\n--- Testing Security Breach (Unauthorized) ---")
    try:
        response = requests.post(f"{BASE_URL}/chat", json={"query": "test"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def get_token():
    print("\n--- Getting Auth Token ---")
    response = requests.post(
        f"{BASE_URL}/auth/token", 
        data={"username": "admin", "password": "aegis2024"}
    )
    token = response.json().get("access_token")
    print(f"Token obtained: {token[:20]}...")
    return token

def test_chat(token, query, label):
    print(f"\n--- Testing {label} ---")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/chat", json={"query": query}, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Answer: {response.json().get('answer', 'NO ANSWER')}")

def test_rate_limit(token):
    print("\n--- Testing Rate Limit (Spamming) ---")
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(12): # Limit is 10
        response = requests.post(f"{BASE_URL}/chat", json={"query": f"spam {i}"}, headers=headers)
        print(f"Req {i+1}: {response.status_code}")
        if response.status_code == 429:
            print("Rate Limit Hit Successfully!")
            print(f"Response: {response.json()}")
            break

if __name__ == "__main__":
    # Wait for server
    time.sleep(3)
    
    test_security_breach()
    token = get_token()
    
    if token:
        test_chat(token, "Who are you and what can you do?", "Simple Question")
        test_chat(token, "Explain the core concepts of a Merger Agreement based on the documents.", "Complex Question")
        test_rate_limit(token)
