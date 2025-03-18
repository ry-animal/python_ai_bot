"""Authentication endpoint for generating tokens."""

from http.server import BaseHTTPRequestHandler
import os
import json
import logging
import time
import jwt
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        path = self.path if hasattr(self, "path") else "Unknown"
        logger.info(f"Request from {client_ip} to {path}")

    def check_api_key(self):
        """Check if the request has a valid API key."""
        api_key = os.environ.get("API_SECRET_KEY")
        if not api_key:
            logger.warning("API_SECRET_KEY not set in environment")
            return True  # Allow if key is not set (for testing)
        
        # Get the API key from the headers
        provided_key = self.headers.get("X-API-Key", "")
        if not provided_key:
            logger.warning("No API key provided in request headers")
            return False
        
        # Simple direct comparison for testing
        return provided_key == api_key
    
    def generate_token(self, user_id, expires_in=3600):
        """Generate a JWT token for the given user_id."""
        jwt_secret = os.environ.get("JWT_SECRET")
        if not jwt_secret:
            logger.warning("JWT_SECRET not set in environment")
            # Return a dummy token for testing
            return {
                "token": "test_token_no_secret",
                "expires_at": str(datetime.now() + timedelta(seconds=expires_in)),
                "expires_in": expires_in
            }
        
        # Create token payload
        now = datetime.now()
        expires_at = now + timedelta(seconds=expires_in)
        
        payload = {
            "sub": user_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + expires_in,
            "iss": "python-ai-bot"
        }
        
        # Sign the token with the secret
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        return {
            "token": token,
            "expires_at": expires_at.isoformat(),
            "expires_in": expires_in
        }

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
    
    def parse_query_parameters(self):
        """Parse query parameters from the request path."""
        query_params = {}
        if not hasattr(self, "path"):
            return query_params
            
        parsed_url = urlparse(self.path)
        parsed_query = parse_qs(parsed_url.query)
        for key, value in parsed_query.items():
            query_params[key] = value[0] if len(value) == 1 else value
        return query_params
    
    def do_GET(self):
        """Handle GET requests for token generation."""
        # Log request info
        self.log_request_info()
        
        if not hasattr(self, "path"):
            self.send_error_response(500, "Internal server error: Missing path attribute")
            return
        
        # Check API key authentication
        if not self.check_api_key():
            self.send_error_response(401, "Unauthorized. Invalid API key.")
            return
        
        # Parse query parameters
        query_params = self.parse_query_parameters()
        
        # Check if user_id is provided
        user_id = query_params.get("user_id", "")
        if not user_id:
            self.send_error_response(400, "Bad request. user_id is required.")
            return
        
        # Generate token
        token_data = self.generate_token(user_id)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(token_data).encode())
    
    def do_POST(self):
        """Handle POST requests for token generation."""
        # Log request info
        self.log_request_info()
        
        if not hasattr(self, "path"):
            self.send_error_response(500, "Internal server error: Missing path attribute")
            return
        
        # Check API key authentication
        if not self.check_api_key():
            self.send_error_response(401, "Unauthorized. Invalid API key.")
            return
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            # Parse JSON body
            body = json.loads(request_body)
            
            # Check if user_id is provided
            user_id = body.get("user_id", "")
            if not user_id:
                self.send_error_response(400, "Bad request. user_id is required.")
                return
            
            # Get token expiration (optional)
            expires_in = body.get("expires_in", 3600)
            
            # Generate token
            token_data = self.generate_token(user_id, expires_in)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(token_data).encode())
            
        except json.JSONDecodeError:
            self.send_error_response(400, "Bad request. Invalid JSON.")
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            self.send_error_response(500, f"Internal server error: {str(e)}") 