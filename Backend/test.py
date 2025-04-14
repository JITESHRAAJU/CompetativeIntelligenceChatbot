import requests
import json

# Base URL - make sure this matches your running server
base_url = "http://localhost:8001"  # Changed to port 8000

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{base_url}/health")
    print("\nHealth Check:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_chat_endpoint():
    """Test the chat endpoint"""
    data = {
        "user_id": "test_user",
        "message": "Tell me about Tesla",
        "industry": "technology",  # Optional
        "competitors": ["Ford", "GM"]  # Optional
    }
    response = requests.post(
        f"{base_url}/chat",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print("\nChat Endpoint:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw Response: {response.text}")

if __name__ == "__main__":
    test_health_check()
    test_chat_endpoint()