"""Vercel serverless function entry point for the Python AI Bot API."""

import sys
import os
import logging
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests

# Add the parent directory to sys.path to allow importing security
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import security module directly
try:
    from api.security import SecureHandlerMixin, validate_input
except ImportError:
    # Fallback if direct import fails - minimal implementation
    class SecureHandlerMixin:
        def add_cors_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'X-API-Key, Content-Type, Authorization')
        
        def log_request_info(self):
            client_ip = self.client_address[0]
            print(f"Request from {client_ip} to {self.path}")
            
        def check_authentication(self):
            return True
            
        def parse_query_parameters(self):
            query_params = {}
            parsed_url = urlparse(self.path)
            parsed_query = parse_qs(parsed_url.query)
            for key, value in parsed_query.items():
                query_params[key] = value[0] if len(value) == 1 else value
            return query_params
            
        def send_error_response(self, status_code, message):
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": message}).encode())
    
    def validate_input(prompt, max_length=1000, min_length=1):
        """Validate input prompt."""
        if not prompt:
            return False, "Prompt is required"
        
        if len(prompt) < min_length:
            return False, f"Prompt must be at least {min_length} characters"
            
        if len(prompt) > max_length:
            return False, f"Prompt must be at most {max_length} characters"
            
        return True, "Valid prompt"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Log environment variables for debugging (excluding sensitive values)
logger.info("Vercel environment: %s", os.environ.get("VERCEL", "Not set"))
logger.info("Environment variables set: %s", list(filter(lambda k: not k.startswith(("OPENAI_", "API_SECRET", "JWT_")), os.environ.keys())))
logger.info("OPENAI_API_KEY set: %s", "Yes" if os.environ.get("OPENAI_API_KEY") else "No")
logger.info("API_SECRET_KEY set: %s", "Yes" if os.environ.get("API_SECRET_KEY") else "No")
logger.info("JWT_SECRET set: %s", "Yes" if os.environ.get("JWT_SECRET") else "No")

class Handler(SecureHandlerMixin, BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        # Handle OPTIONS requests for CORS
        if self.command == 'OPTIONS':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            return
        
        # Check authentication
        is_authenticated, error_message, status_code = self.check_authentication()
        if not is_authenticated:
            self.send_error_response(status_code, error_message)
            return
        
        # Get API key
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Parse query parameters
        query_params = self.parse_query_parameters()
        
        # Handle request based on path
        if self.path.startswith("/generate-debug"):
            # Handle OpenAI test with prompt validation
            prompt = query_params.get("prompt", "Tell me a short joke")
            is_valid, error_message = validate_input(prompt)
            
            if not is_valid:
                self.send_error_response(400, error_message)
                return
                
            response = self._handle_openai_test(prompt)
        elif self.path.startswith("/auth/token"):
            # Handle token generation (for demo/testing purposes only)
            # In production, you would have a proper authentication flow
            user_id = query_params.get("user_id")
            if not user_id:
                self.send_error_response(400, "Missing user_id parameter")
                return
                
            token = self.jwt_auth.generate_token(user_id)
            if not token:
                self.send_error_response(500, "Failed to generate token")
                return
                
            response = {"token": token}
        elif self.path == "/health":
            # Simple health check endpoint
            response = {"status": "ok"}
        else:
            # Default response
            response = {
                "message": "Python AI Bot API",
                "api_key_set": "Yes" if api_key else "No",
                "api_key_length": len(api_key) if api_key else 0,
                "vercel": os.environ.get("VERCEL", "Not set")
            }
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        # Handle OPTIONS requests for CORS
        if self.command == 'OPTIONS':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            return
        
        # Check authentication
        is_authenticated, error_message, status_code = self.check_authentication()
        if not is_authenticated:
            self.send_error_response(status_code, error_message)
            return
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request_json = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON")
            return
        
        # Handle request based on path
        if self.path.startswith("/generate"):
            # Handle OpenAI generation with prompt validation
            prompt = request_json.get("prompt")
            is_valid, error_message = validate_input(prompt)
            
            if not is_valid:
                self.send_error_response(400, error_message)
                return
                
            response = self._handle_openai_test(prompt)
        else:
            self.send_error_response(404, "Not found")
            return
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
    
    def _handle_openai_test(self, prompt="Tell me a short joke"):
        """Handle OpenAI test."""
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            return {"error": "No OpenAI API key found in environment"}
        
        # Fall back to using direct API request
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 100
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return {
                    "text": content,
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