"""Extremely simple OpenAI test."""

from http.server import BaseHTTPRequestHandler
import os
import json
import sys

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        api_key = os.environ.get("OPENAI_API_KEY")
        
        response = {
            "api_key_length": len(api_key) if api_key else 0,
            "api_key_set": "Yes" if api_key else "No",
            "python_version": sys.version,
            "sys_path": sys.path
        }
        
        try:
            # First try to import OpenAI
            import openai
            response["openai_version"] = openai.__version__
            
            # Only continue if we have an API key
            if api_key:
                # Try the simplest possible client initialization
                client = openai.OpenAI(api_key=api_key)
                response["client_initialized"] = "Yes"
                
                # Use a very basic request with minimal parameters
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Tell me a short joke"}]
                )
                response["success"] = True
                response["content"] = completion.choices[0].message.content
        except Exception as e:
            response["error"] = str(e)
            response["error_type"] = type(e).__name__
        
        self.wfile.write(json.dumps(response).encode()) 