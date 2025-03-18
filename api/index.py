"""Main handler for API requests."""

from http.server import BaseHTTPRequestHandler
import os
import json
import logging
import requests
import time
import jwt
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log environment variables (excluding sensitive ones)
env_vars = {k: v for k, v in os.environ.items() if not k.lower().__contains__('key') and not k.lower().__contains__('secret')}
logger.info(f"Environment variables: {env_vars}")

class Handler(BaseHTTPRequestHandler):
    def add_cors_headers(self):
        """Add CORS headers to the response."""
        # Get allowed origins from env, default to '*' for development
        allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
        origin = self.headers.get("Origin", "")
        
        # If specific origins are set, check if the request origin is allowed
        if allowed_origins != "*" and origin:
            allowed_origin_list = allowed_origins.split(",")
            if origin in allowed_origin_list:
                self.send_header("Access-Control-Allow-Origin", origin)
            else:
                self.send_header("Access-Control-Allow-Origin", allowed_origin_list[0])
        else:
            # In development or if all origins are allowed
            self.send_header("Access-Control-Allow-Origin", "*")
            
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-API-Key, Content-Type, Authorization")
    
    def log_request_info(self):
        """Log information about the request."""
        client_ip = self.client_address[0] if hasattr(self, "client_address") else "Unknown"
        logger.info(f"Request from {client_ip} to {self.path}")

    def check_authentication(self):
        """Check if the request is authenticated."""
        # Get authentication method from query params or headers
        auth_header = self.headers.get("Authorization", "")
        
        # Check for API key authentication
        api_key = os.environ.get("API_SECRET_KEY")
        provided_key = self.headers.get("X-API-Key", "")
        
        if api_key and provided_key and provided_key == api_key:
            return True
        
        # Check for JWT authentication
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            return self.verify_token(token)
        
        # If API_SECRET_KEY is not set, allow access (for testing)
        if not api_key:
            logger.warning("API_SECRET_KEY not set in environment")
            return True
            
        return False
    
    def verify_token(self, token):
        """Verify a JWT token."""
        jwt_secret = os.environ.get("JWT_SECRET")
        if not jwt_secret:
            logger.warning("JWT_SECRET not set in environment")
            return False
            
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            # Check if token is expired
            if "exp" in payload and payload["exp"] < time.time():
                return False
            return True
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return False
    
    def validate_input(self, prompt, max_length=1000, min_length=1):
        """Validate input prompt."""
        if not prompt:
            return False, "Prompt is required"
        
        if len(prompt) < min_length:
            return False, f"Prompt must be at least {min_length} characters"
            
        if len(prompt) > max_length:
            return False, f"Prompt must be at most {max_length} characters"
            
        return True, "Valid prompt"
    
    def parse_query_parameters(self):
        """Parse query parameters from the request path."""
        query_params = {}
        parsed_url = urlparse(self.path)
        parsed_query = parse_qs(parsed_url.query)
        for key, value in parsed_query.items():
            query_params[key] = value[0] if len(value) == 1 else value
        return query_params

    def send_error_response(self, status_code, message):
        """Send an error response to the client."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.add_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        # Log request info
        self.log_request_info()
        
        # Parse URL path
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Handle health check
        if path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
            return
            
        # Check authentication for other endpoints
        if not self.check_authentication():
            self.send_error_response(401, "Unauthorized")
            return
            
        # Handle /generate-debug endpoint
        if path == "/generate-debug":
            self._handle_generate_debug()
            return
            
        # Handle unknown endpoints
        self.send_error_response(404, "Not found")
    
    def _handle_generate_debug(self):
        """Handle /generate-debug endpoint."""
        query_params = self.parse_query_parameters()
        prompt = query_params.get("prompt", "")
        use_mock_fallback = query_params.get("use_mock_fallback", "true").lower() == "true"
        
        # Validate prompt
        is_valid, message = self.validate_input(prompt)
        if not is_valid:
            self.send_error_response(400, message)
            return
            
        # Generate text
        try:
            if use_mock_fallback:
                text = f"This is a mock response for: {prompt}"
            else:
                text = self._generate_text_with_openai(prompt)
                
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"text": text}).encode())
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            self.send_error_response(500, f"Error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests."""
        # Log request info
        self.log_request_info()
        
        # Parse URL path
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Check authentication
        if not self.check_authentication():
            self.send_error_response(401, "Unauthorized")
            return
            
        # Handle /generate endpoint
        if path == "/generate":
            self._handle_generate_post()
            return
            
        # Handle unknown endpoints
        self.send_error_response(404, "Not found")
    
    def _handle_generate_post(self):
        """Handle /generate POST endpoint."""
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request_json = json.loads(post_data.decode('utf-8'))
            prompt = request_json.get("prompt", "")
            use_mock_fallback = request_json.get("use_mock_fallback", True)
            
            # Validate prompt
            is_valid, message = self.validate_input(prompt)
            if not is_valid:
                self.send_error_response(400, message)
                return
                
            # Generate text
            try:
                if use_mock_fallback:
                    text = f"This is a mock response for: {prompt}"
                else:
                    text = self._generate_text_with_openai(prompt)
                    
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.add_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"text": text}).encode())
            except Exception as e:
                logger.error(f"Error generating text: {str(e)}")
                self.send_error_response(500, f"Error: {str(e)}")
                
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON")
    
    def _generate_text_with_openai(self, prompt):
        """Generate text using OpenAI API."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not set")
            
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
            "max_tokens": 150
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise Exception(f"Failed to generate text: {str(e)}") 