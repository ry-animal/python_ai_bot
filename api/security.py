"""Security module for API authentication and rate limiting."""

import os
import time
import json
import logging
import jwt
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Simple in-memory rate limiter
class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, limit=10, window=60):
        """Initialize rate limiter.
        
        Args:
            limit (int): Maximum number of requests allowed in the window.
            window (int): Time window in seconds.
        """
        self.limit = limit
        self.window = window
        self.records = {}  # {client_ip: [(timestamp1), (timestamp2), ...]}
    
    def is_rate_limited(self, client_ip):
        """Check if a client is rate limited.
        
        Args:
            client_ip (str): Client IP address.
            
        Returns:
            bool: True if rate limited, False otherwise.
        """
        current_time = time.time()
        
        if client_ip not in self.records:
            self.records[client_ip] = []
        
        # Remove old timestamps
        self.records[client_ip] = [t for t in self.records[client_ip] 
                                if current_time - t < self.window]
        
        # Check if limit reached
        if len(self.records[client_ip]) >= self.limit:
            return True
        
        # Add new timestamp
        self.records[client_ip].append(current_time)
        return False

# JWT Authentication
class JWTAuth:
    """JWT Authentication for API requests."""
    
    def __init__(self, secret_key=None):
        """Initialize JWT authentication.
        
        Args:
            secret_key (str, optional): Secret key for JWT. Defaults to None,
                in which case it will be read from JWT_SECRET environment variable.
        """
        self.secret_key = secret_key or os.environ.get("JWT_SECRET")
        
        if not self.secret_key:
            logger.warning("No JWT secret key provided. JWT auth will fail.")
    
    def generate_token(self, user_id, expires_in=3600):
        """Generate a JWT token.
        
        Args:
            user_id (str): User ID to encode in the token.
            expires_in (int, optional): Expiration time in seconds. Defaults to 3600 (1 hour).
            
        Returns:
            str: JWT token or None if secret key is missing.
        """
        if not self.secret_key:
            return None
        
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify a JWT token.
        
        Args:
            token (str): JWT token to verify.
            
        Returns:
            dict: Decoded payload if token is valid, None otherwise.
        """
        if not self.secret_key:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None

# API Key Authentication
class APIKeyAuth:
    """API Key Authentication for API requests."""
    
    def __init__(self, api_key=None):
        """Initialize API Key authentication.
        
        Args:
            api_key (str, optional): API key for authentication. Defaults to None,
                in which case it will be read from API_SECRET_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("API_SECRET_KEY")
        
        if not self.api_key:
            logger.warning("No API key provided. API key auth will fail.")
    
    def verify_key(self, provided_key):
        """Verify an API key.
        
        Args:
            provided_key (str): API key to verify.
            
        Returns:
            bool: True if key is valid, False otherwise.
        """
        if not self.api_key:
            return False
        
        return provided_key == self.api_key

# Input validation
def validate_input(prompt, max_length=1000, min_length=1):
    """Validate input prompt.
    
    Args:
        prompt (str): The input prompt to validate.
        max_length (int, optional): Maximum allowed length. Defaults to 1000.
        min_length (int, optional): Minimum allowed length. Defaults to 1.
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not prompt or len(prompt) < min_length:
        return False, "Prompt too short or empty"
    
    if len(prompt) > max_length:
        return False, f"Prompt too long (max {max_length} characters)"
    
    # Add more validations as needed
    # Example: Check for harmful content, etc.
    
    return True, None

# Secure handler mixin
class SecureHandlerMixin:
    """Mixin for adding security to BaseHTTPRequestHandler."""
    
    def __init__(self):
        """Initialize security components."""
        self.rate_limiter = RateLimiter()
        self.jwt_auth = JWTAuth()
        self.api_key_auth = APIKeyAuth()
    
    def send_error_response(self, status_code, message):
        """Send error response.
        
        Args:
            status_code (int): HTTP status code.
            message (str): Error message.
        """
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def add_cors_headers(self):
        """Add CORS headers to response."""
        allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
        self.send_header('Access-Control-Allow-Origin', allowed_origins)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
    
    def log_request_info(self):
        """Log request information."""
        client_ip = self.client_address[0]
        request_path = self.path
        user_agent = self.headers.get('User-Agent', 'Unknown')
        logger.info(f"Request from {client_ip}: {request_path} (User-Agent: {user_agent})")
    
    def parse_query_parameters(self):
        """Parse query parameters from path.
        
        Returns:
            dict: Query parameters.
        """
        parsed_url = urlparse(self.path)
        return {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
    
    def check_authentication(self):
        """Check if request is authenticated.
        
        Returns:
            tuple: (is_authenticated, error_message, status_code)
        """
        self.log_request_info()
        
        # Check rate limiting
        client_ip = self.client_address[0]
        if self.rate_limiter.is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return False, "Rate limit exceeded", 429
        
        # First try JWT token from Authorization header
        auth_header = self.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = self.jwt_auth.verify_token(token)
            if payload:
                logger.info(f"Authenticated with JWT token for user {payload.get('user_id')}")
                return True, None, 200
        
        # Then try API key from X-API-Key header
        api_key = self.headers.get('X-API-Key')
        if api_key and self.api_key_auth.verify_key(api_key):
            logger.info(f"Authenticated with API key from {client_ip}")
            return True, None, 200
        
        # If both methods fail
        allowed_path_prefixes = ['/api/test', '/health']
        if any(self.path.startswith(prefix) for prefix in allowed_path_prefixes):
            # Public endpoints don't require authentication
            return True, None, 200
        
        logger.warning(f"Authentication failed for {client_ip}")
        return False, "Unauthorized", 401 