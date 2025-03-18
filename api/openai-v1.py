"""Test endpoint for OpenAI v1.0+ API."""

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
        
        if not api_key:
            response = {
                "error": "No OpenAI API key found in environment"
            }
        else:
            response = {
                "api_key_length": len(api_key),
                "api_key_set": "Yes",
                "python_version": sys.version
            }
            
            try:
                # Import OpenAI
                import openai
                response["openai_version"] = openai.__version__
                
                # Initialize client (v1 style)
                client = openai.OpenAI(api_key=api_key)
                response["client_initialized"] = True
                
                # Make a simple request (v1 style)
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Tell me a short joke."}
                    ],
                    max_tokens=50
                )
                
                response["success"] = True
                response["joke"] = completion.choices[0].message.content
                
            except Exception as e:
                response["error"] = str(e)
                response["error_type"] = type(e).__name__
        
        self.wfile.write(json.dumps(response).encode()) 