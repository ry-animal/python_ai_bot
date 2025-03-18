"""Vercel serverless function entry point for the Python AI Bot API."""

import sys
import os
import logging
import json
from http.server import BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Log environment variables for debugging (excluding sensitive values)
logger.info("Vercel environment: %s", os.environ.get("VERCEL", "Not set"))
logger.info("Environment variables set: %s", list(filter(lambda k: not k.startswith("OPENAI_"), os.environ.keys())))
logger.info("OPENAI_API_KEY set: %s", "Yes" if os.environ.get("OPENAI_API_KEY") else "No")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if self.path.startswith("/generate-debug"):
            # Handle OpenAI test
            response = self._handle_openai_test()
        else:
            # Default response
            response = {
                "message": "Python AI Bot API",
                "api_key_set": "Yes" if api_key else "No",
                "api_key_length": len(api_key) if api_key else 0,
                "vercel": os.environ.get("VERCEL", "Not set")
            }
            
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_openai_test(self):
        """Handle OpenAI test."""
        import importlib.util
        import sys
        import requests
        
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            return {"error": "No OpenAI API key found in environment"}
        
        # Fall back to using direct API request if OpenAI client fails
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Tell me a short joke."}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                joke = response.json()["choices"][0]["message"]["content"]
                return {
                    "text": joke,
                    "success": True,
                    "method": "direct_api"
                }
            else:
                return {
                    "text": f"API Error: {response.status_code} - {response.text}",
                    "error_type": "APIError",
                    "method": "direct_api"
                }
        except Exception as e:
            logger.error(f"Error with direct API request: {str(e)}")
            return {
                "text": f"Error with direct API request: {str(e)}",
                "error_type": type(e).__name__,
                "method": "direct_api"
            } 