"""Test OpenAI API directly."""

import os
import json
import requests

# Load environment variables from .env.local
def load_env():
    """Load environment variables from .env.local."""
    if os.path.exists(".env.local"):
        with open(".env.local") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
                    print(f"Loaded environment variable: {key}")

# Load environment variables
load_env()

def test_openai_api(prompt="Tell me a joke"):
    """Test the OpenAI API directly."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set in environment")
        return False
        
    print(f"API Key length: {len(api_key)}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150
    }
    
    try:
        print("Calling OpenAI API...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print("\nAPI Response:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            return True
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API...")
    success = test_openai_api()
    if success:
        print("\n✅ OpenAI API test successful!")
    else:
        print("\n❌ OpenAI API test failed!") 