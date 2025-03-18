"""Simple direct test for the API."""

from http.server import BaseHTTPRequestHandler
import os
import json
import requests

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Default response with environment info
        response = {
            "message": "Environment Info",
            "api_key_set": "Yes" if api_key else "No",
            "api_key_length": len(api_key) if api_key else 0,
            "vercel": os.environ.get("VERCEL", "Not set"),
            "env_keys": list(os.environ.keys())
        }
        
        # If the path contains 'openai', test the OpenAI API
        if 'openai' in self.path:
            try:
                if not api_key:
                    response["openai_test"] = "Skipped - No API key"
                else:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }
                    
                    payload = {
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "Hello! Give me a one-sentence response."}
                        ],
                        "max_tokens": 50
                    }
                    
                    api_response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                    if api_response.status_code == 200:
                        response["openai_test"] = "Success"
                        response["openai_response"] = api_response.json()["choices"][0]["message"]["content"]
                    else:
                        response["openai_test"] = "Failed"
                        response["openai_error"] = f"{api_response.status_code}: {api_response.text}"
            except Exception as e:
                response["openai_test"] = "Error"
                response["openai_error"] = str(e)
        
        self.wfile.write(json.dumps(response).encode()) 