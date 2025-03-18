"""Test endpoint for OpenAI v0.28 API."""

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
                # Import OpenAI
                import openai
                
                # Set up the API key
                openai.api_key = api_key
                
                # Print version for debugging
                response = {
                    "openai_version": openai.__version__,
                    "api_key_length": len(api_key)
                }
                
                # Use the v0.x syntax
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Tell me a short joke."}
                    ],
                    max_tokens=50
                )
                
                response["success"] = True
                response["content"] = completion.choices[0].message.content
                
            except Exception as e:
                response = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "api_key_length": len(api_key)
                }
        
        self.wfile.write(json.dumps(response).encode()) 