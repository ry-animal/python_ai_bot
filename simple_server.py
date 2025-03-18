"""Simple direct HTTP server for testing our API."""

import os
import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

# Load environment variables
def load_env():
    """Load environment variables from .env.local."""
    if os.path.exists(".env.local"):
        with open(".env.local") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
                    print(f"Loaded environment variable: {key}")

# Import directly from our API files
from api.direct_test import Handler as DirectTestHandler
from api.index import Handler as IndexHandler

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    """Simple handler that routes requests to the appropriate handler."""
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/api/test":
            # Use DirectTestHandler
            handler = DirectTestHandler(self.request, self.client_address, self.server)
            handler.do_GET()
        elif path.startswith("/generate-debug"):
            # Use IndexHandler
            handler = IndexHandler(self.request, self.client_address, self.server)
            handler.do_GET()
        else:
            # Default response
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": f"Path not found: {path}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/generate":
            # Use IndexHandler
            handler = IndexHandler(self.request, self.client_address, self.server)
            handler.do_POST()
        else:
            # Default response
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": f"Path not found: {path}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-API-Key, Content-Type, Authorization")
        self.end_headers()

def run_server(port=8000):
    """Run the test server."""
    # Make sure port is not in use
    try:
        server_address = ('', port)
        httpd = socketserver.TCPServer(server_address, SimpleHandler)
        print(f"Starting simple server on port {port}...")
        print(f"Test the API with: curl -H 'X-API-Key: {os.environ.get('API_SECRET_KEY')}' http://localhost:{port}/api/test")
        print(f"Test text generation: curl -H 'X-API-Key: {os.environ.get('API_SECRET_KEY')}' http://localhost:{port}/generate-debug?prompt=Hello")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {port} is already in use. Please stop any existing servers or use a different port.")
            print("You can try: pkill -f 'python simple_server.py'")
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    # Load environment variables
    load_env()
    
    # Run server
    run_server() 