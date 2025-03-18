"""Test endpoint for OpenAI with no extra parameters."""

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
            "python_version": sys.version
        }
        
        try:
            # First try to import OpenAI
            import openai
            response["openai_version"] = openai.__version__
            
            # Only initialize with the API key, no other parameters
            if api_key:
                client = openai.OpenAI(api_key=api_key)
                response["client_initialized"] = "Yes"
                
                # Keep it extremely simple with minimal parameters
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}]
                )
                
                response["success"] = True
                response["content"] = completion.choices[0].message.content
        except Exception as e:
            response["error"] = str(e)
            response["error_type"] = type(e).__name__
        
        self.wfile.write(json.dumps(response).encode()) 