"""Simple test for Vercel environment variables."""

from http.server import BaseHTTPRequestHandler
import os
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "message": "Environment Info",
            "api_key_set": "Yes" if os.environ.get("OPENAI_API_KEY") else "No",
            "api_key_length": len(os.environ.get("OPENAI_API_KEY", "")) if os.environ.get("OPENAI_API_KEY") else 0,
            "vercel": os.environ.get("VERCEL", "Not set"),
            "env_keys": list(filter(lambda k: not k.startswith("OPENAI_"), os.environ.keys()))
        }
        
        self.wfile.write(json.dumps(response).encode()) 