"""Simple direct test for the API."""

from http.server import BaseHTTPRequestHandler
import os
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Handler(BaseHTTPRequestHandler):
    def add_cors_headers(self):
        """Add CORS headers to the response."""
        # Get allowed origins from env, default to '*' for development
        allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
        origin = self.headers.get("Origin", "")
        
        # If specific origins are set, check if the request origin is allowed
        if allowed_origins != "*" and origin:
            allowed_origin_list = allowed_origins.split(",")
            if origin in allowed_origin_list:
                self.send_header("Access-Control-Allow-Origin", origin)
            else:
                self.send_header("Access-Control-Allow-Origin", allowed_origin_list[0])
        else:
            # In development or if all origins are allowed
            self.send_header("Access-Control-Allow-Origin", "*")
            
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-API-Key, Content-Type, Authorization")
    
    def log_request_info(self):
        """Log information about the request."""
        client_ip = self.client_address[0] if hasattr(self, "client_address") else "Unknown"
        logger.info(f"Request from {client_ip} to {self.path}")
    
    def check_authentication(self):
        """Check if the request is authenticated."""
        api_key = os.environ.get("API_SECRET_KEY")
        if not api_key:
            logger.warning("API_SECRET_KEY not set in environment")
            return True  # Allow if key is not set (for testing)
        
        # Get the API key from the headers
        provided_key = self.headers.get("X-API-Key", "")
        if not provided_key:
            logger.warning("No API key provided in request headers")
            return False
        
        # Simple direct comparison for testing
        return provided_key == api_key
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.add_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        # Log request info
        self.log_request_info()
        
        # Check authentication
        if not self.check_authentication():
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized. Invalid API key."}).encode())
            return
        
        # Add headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Default response with environment info
        response = {
            "message": "Environment Info",
            "api_key_set": "Yes" if api_key else "No",
            "api_key_length": len(api_key) if api_key else 0,
            "vercel": os.environ.get("VERCEL", "Not set"),
            "env_keys": [k for k in os.environ.keys() if not k.lower().__contains__('key') and not k.lower().__contains__('secret')]
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