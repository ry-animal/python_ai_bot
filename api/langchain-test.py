"""Simple test using LangChain with OpenAI."""

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
                # Import LangChain components
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage, SystemMessage
                
                # Initialize the chat model
                model = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    openai_api_key=api_key,
                    max_tokens=50
                )
                
                # Create messages
                messages = [
                    SystemMessage(content="You are a helpful assistant. Provide a short joke."),
                    HumanMessage(content="Tell me a simple joke.")
                ]
                
                # Get response
                ai_response = model.invoke(messages)
                
                response = {
                    "success": True,
                    "model": "gpt-3.5-turbo",
                    "joke": ai_response.content,
                    "api_key_length": len(api_key)
                }
            except Exception as e:
                response = {
                    "error": str(e),
                    "api_key_length": len(api_key)
                }
        
        self.wfile.write(json.dumps(response).encode()) 