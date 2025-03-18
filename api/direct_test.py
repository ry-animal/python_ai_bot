"""Simple direct test for the API."""

from http.server import BaseHTTPRequestHandler
import os
import json
import requests
import sys
import importlib.util

# Add the parent directory to sys.path to allow importing security
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import security module directly
try:
    from api.security import SecureHandlerMixin
except ImportError:
    # Fallback if direct import fails
    # Define a minimal version of SecureHandlerMixin
    class SecureHandlerMixin:
        def add_cors_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'X-API-Key, Content-Type, Authorization')
        
        def log_request_info(self):
            client_ip = self.client_address[0]
            print(f"Request from {client_ip} to {self.path}")

class Handler(SecureHandlerMixin, BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        # Add CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        
        # Log request info
        self.log_request_info()
        
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