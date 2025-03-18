"""Test API handlers directly without starting a server."""

import os
import json
import io
import sys
from urllib.parse import parse_qs
from http.client import HTTPResponse
import unittest
from unittest.mock import MagicMock

# Load environment variables from .env.local
def load_env():
    """Load environment variables from .env.local."""
    if os.path.exists(".env.local"):
        with open(".env.local") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
                    print(f"Loaded environment variable: {key}")

# Load environment variables
load_env()

# Import the handlers
from api.direct_test import Handler as DirectTestHandler
from api.index import Handler as IndexHandler

class MockHTTPResponse(HTTPResponse):
    def __init__(self):
        self.headers = {}
        self.status_code = None
        self.response_body = None
        
    def send_response(self, code):
        self.status_code = code
        
    def send_header(self, key, value):
        self.headers[key] = value
        
    def end_headers(self):
        pass
        
    def write(self, data):
        self.response_body = data

class MockSocket:
    def makefile(self, *args, **kwargs):
        return io.BytesIO()

class MockRequest:
    def __init__(self, method="GET", path="/", body=None, headers=None):
        self.method = method
        self.path = path
        self.body = body or ""
        self.headers = headers or {}
        
    def to_mock_handler(self, handler_class):
        # Create mock objects
        mock_socket = MockSocket()
        mock_request = MagicMock()
        mock_server = MagicMock()
        mock_client_address = ("127.0.0.1", 12345)
        
        # Create the handler
        handler = handler_class(mock_request, mock_client_address, mock_server)
        
        # Mock the request attributes
        handler.command = self.method
        handler.path = self.path
        handler.headers = MagicMock()
        handler.headers.get = lambda key, default="": self.headers.get(key, default)
        
        # Mock the response methods
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        handler.wfile.write = MagicMock()
        
        # If it's a POST request, set up the request body
        if self.method == "POST":
            handler.rfile = io.BytesIO(self.body.encode("utf-8"))
            handler.headers.get = lambda key, default="": str(len(self.body)) if key == "Content-Length" else self.headers.get(key, default)
            
        return handler

def test_direct_test_endpoint():
    """Test the /api/test endpoint."""
    # Create the request
    request = MockRequest(
        method="GET",
        path="/api/test",
        headers={"X-API-Key": os.environ.get("API_SECRET_KEY")}
    )
    
    # Create the handler
    handler = request.to_mock_handler(DirectTestHandler)
    
    # Call the method
    handler.do_GET()
    
    # Get the response
    response_data = handler.wfile.write.call_args[0][0]
    
    # Decode and parse the JSON
    response_json = json.loads(response_data.decode("utf-8"))
    
    # Print the result
    print("==== /api/test Response ====")
    print(json.dumps(response_json, indent=2))
    print()
    
    return response_json

def test_generate_endpoint(prompt="Hello, world!"):
    """Test the /generate-debug endpoint."""
    # Create the request
    request = MockRequest(
        method="GET",
        path=f"/generate-debug?prompt={prompt}",
        headers={"X-API-Key": os.environ.get("API_SECRET_KEY")}
    )
    
    # Create the handler
    handler = request.to_mock_handler(IndexHandler)
    
    # Call the method
    handler.do_GET()
    
    # Get the response
    response_data = handler.wfile.write.call_args[0][0]
    
    # Decode and parse the JSON
    response_json = json.loads(response_data.decode("utf-8"))
    
    # Print the result
    print(f"==== /generate-debug?prompt={prompt} Response ====")
    print(json.dumps(response_json, indent=2))
    print()
    
    return response_json

if __name__ == "__main__":
    # Make sure the API key is set
    if not os.environ.get("API_SECRET_KEY"):
        print("API_SECRET_KEY not set in environment")
        sys.exit(1)
        
    # Run the tests
    test_direct_test_endpoint()
    test_generate_endpoint(prompt="Tell me a joke") 