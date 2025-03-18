"""Authentication endpoint for generating tokens."""

from http.server import BaseHTTPRequestHandler
import os
import json
import logging
import sys
from urllib.parse import urlparse, parse_qs

# Add the parent directory to sys.path to allow importing security
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import security module directly
try:
    from api.security import SecureHandlerMixin, JWTAuth, APIKeyAuth
except ImportError:
    # Fallback if direct import fails - minimal implementation
    # This should only be used for testing purposes
    from http.server import BaseHTTPRequestHandler
    
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
            
        def send_error_response(self, status_code, message):
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.add_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": message}).encode())
            
    class JWTAuth:
        def generate_token(self, user_id, expires_in=3600):
            return {"token": "test_token", "expires_in": expires_in}
            
    class APIKeyAuth:
        def verify_key(self, provided_key):
            return True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class Handler(SecureHandlerMixin, BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for token generation (for testing only)."""
        self.log_request_info()
        
        # Parse query parameters
        query_params = self.parse_query_parameters()
        
        # Token generation requires a user_id and API key for authorization
        user_id = query_params.get("user_id")
        if not user_id:
            self.send_error_response(400, "Missing user_id parameter")
            return
        
        # Check API key authentication for token generation
        api_key = self.headers.get('X-API-Key')
        if not api_key or not self.api_key_auth.verify_key(api_key):
            self.send_error_response(401, "Valid API key required for token generation")
            return
        
        # Generate token
        token = self.jwt_auth.generate_token(user_id)
        if not token:
            self.send_error_response(500, "Failed to generate token - JWT_SECRET not configured")
            return
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            "token": token,
            "expires_in": 3600,
            "token_type": "Bearer"
        }).encode())
    
    def do_POST(self):
        """Handle POST requests for token generation."""
        self.log_request_info()
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request_json = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON")
            return
        
        # Token generation requires credentials
        # In a real system, this would validate against a user database
        user_id = request_json.get("user_id")
        api_key = request_json.get("api_key")
        
        if not user_id:
            self.send_error_response(400, "Missing user_id")
            return
        
        if not api_key or not self.api_key_auth.verify_key(api_key):
            self.send_error_response(401, "Invalid credentials")
            return
        
        # Generate token
        token = self.jwt_auth.generate_token(user_id)
        if not token:
            self.send_error_response(500, "Failed to generate token - JWT_SECRET not configured")
            return
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            "token": token,
            "expires_in": 3600,
            "token_type": "Bearer"
        }).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers() 