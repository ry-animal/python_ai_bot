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
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            return {"error": "No OpenAI API key found in environment"}
        
        try:
            # Import OpenAI directly
            # This ensures we're using the installed package, not any local module
            import importlib
            openai = importlib.import_module('openai')
            
            try:
                # Initialize the client with minimal arguments and exception handling
                logger.info("Initializing OpenAI client")
                kwargs = {"api_key": api_key}
                
                # Create client with only api_key
                client = openai.OpenAI(**kwargs)
                
                # Successfully created client
                logger.info("Successfully created OpenAI client")
                
                # Make a simple request
                logger.info("Making chat completion request")
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Tell me a short joke."}
                    ],
                    max_tokens=50
                )
                
                joke = completion.choices[0].message.content
                return {
                    "text": joke,
                    "success": True
                }
            except TypeError as e:
                logger.error(f"TypeError initializing client: {str(e)}")
                if "proxies" in str(e):
                    return {
                        "text": "Error initializing client due to proxies issue",
                        "error_detail": str(e),
                        "error_type": "TypeError",
                        "openai_version": openai.__version__
                    }
                return {
                    "text": f"Error: {str(e)}",
                    "error_type": "TypeError",
                    "openai_version": openai.__version__
                }
            except Exception as e:
                logger.error(f"Error making chat completion: {str(e)}")
                return {
                    "text": f"Error in chat completion: {str(e)}",
                    "error_type": type(e).__name__,
                    "openai_version": openai.__version__
                }
        except ImportError as e:
            logger.error(f"ImportError: {str(e)}")
            return {
                "text": f"Error importing OpenAI: {str(e)}",
                "error_type": "ImportError"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "text": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__
            } 