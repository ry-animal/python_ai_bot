"""Simple direct test for OpenAI."""

from http.server import BaseHTTPRequestHandler
import os
import json

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
            try:
                # Using the newer OpenAI client
                import openai
                
                # Direct initialization without proxies
                client = openai.OpenAI(api_key=api_key)
                
                # Try a simple completion
                openai_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Tell me a simple joke."}
                    ],
                    max_tokens=50
                )
                
                joke = openai_response.choices[0].message.content.strip()
                response = {
                    "success": True,
                    "model": "gpt-3.5-turbo",
                    "joke": joke,
                    "api_key_length": len(api_key)
                }
            except Exception as e:
                response = {
                    "error": str(e),
                    "api_key_length": len(api_key),
                    "openai_version": openai.__version__ if 'openai' in globals() else "Not loaded"
                }
        
        self.wfile.write(json.dumps(response).encode()) 