"""Super simple HTTP server for testing."""

import os
import json
import http.server
import socketserver
import logging
import requests
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    """Very simple handler with no dependencies."""
    
    def log_request(self, code='-', size='-'):
        # Override to provide more useful request logging
        logger.info(f"{self.command} {self.path} - {code}")
    
    def do_GET(self):
        """Handle GET requests."""
        # Parse URL path
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Parse query parameters
        query_params = {}
        parsed_query = parse_qs(parsed_path.query)
        for key, value in parsed_query.items():
            query_params[key] = value[0] if len(value) == 1 else value
        
        # Check API key authentication
        api_key = os.environ.get("API_SECRET_KEY")
        provided_key = self.headers.get("X-API-Key", "")
        
        if api_key and provided_key != api_key:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized. Invalid API key."}).encode())
            return
        
        # Handle test endpoint
        if path == "/api/test":
            self._handle_test()
        # Handle generate endpoint
        elif path == "/generate-debug":
            self._handle_generate(query_params)
        # Handle health check
        elif path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        # Handle unknown endpoints
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Not found: {path}"}).encode())
    
    def _handle_test(self):
        """Handle /api/test endpoint."""
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Create response
        response = {
            "message": "Environment Info",
            "api_key_set": "Yes" if api_key else "No",
            "api_key_length": len(api_key) if api_key else 0,
            "vercel": os.environ.get("VERCEL", "Not set"),
            "env_keys": [k for k in os.environ.keys() if not k.lower().__contains__('key') and not k.lower().__contains__('secret')]
        }
        
        # If the path contains 'openai', test the OpenAI API
        if 'openai' in self.path:
            try:
                if not api_key:
                    response["openai_test"] = "Skipped - No API key"
                else:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }
                    
                    payload = {
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "Hello! Give me a one-sentence response."}
                        ],
                        "max_tokens": 50
                    }
                    
                    api_response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                    if api_response.status_code == 200:
                        response["openai_test"] = "Success"
                        response["openai_response"] = api_response.json()["choices"][0]["message"]["content"]
                    else:
                        response["openai_test"] = "Failed"
                        response["openai_error"] = f"{api_response.status_code}: {api_response.text}"
            except Exception as e:
                response["openai_test"] = "Error"
                response["openai_error"] = str(e)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_generate(self, query_params):
        """Handle /generate-debug endpoint."""
        prompt = query_params.get("prompt", "")
        use_mock_fallback = query_params.get("use_mock_fallback", "true").lower() == "true"
        
        # Validate prompt
        if not prompt:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Prompt is required"}).encode())
            return
        
        # Generate text
        try:
            if use_mock_fallback:
                text = f"This is a mock response for: {prompt}"
            else:
                # Call OpenAI API
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
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    text = response.json()["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
                
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"text": text}).encode())
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-API-Key, Content-Type, Authorization')
        self.end_headers()

def run_server(port=8000):
    """Run the test server."""
    try:
        # Make sure port is free
        socketserver.TCPServer.allow_reuse_address = True
        server_address = ('', port)
        httpd = socketserver.TCPServer(server_address, SimpleHandler)
        logger.info(f"Starting simple server on port {port}...")
        logger.info(f"Test the API with: curl -H 'X-API-Key: {os.environ.get('API_SECRET_KEY')}' http://localhost:{port}/api/test")
        logger.info(f"Test text generation: curl -H 'X-API-Key: {os.environ.get('API_SECRET_KEY')}' http://localhost:{port}/generate-debug?prompt=Hello")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logger.info("Starting simple test server...")
    run_server() 