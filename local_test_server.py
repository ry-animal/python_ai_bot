"""Local test server for Vercel functions."""
import http.server
import importlib.util
import os
import sys
import json
import socketserver
from urllib.parse import urlparse, parse_qs

# Add the current directory to sys.path to allow importing modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Load environment variables from .env.local
def load_dotenv():
    """Load environment variables from .env.local."""
    if os.path.exists(".env.local"):
        with open(".env.local") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
                    print(f"Loaded environment variable: {key}")

def load_module_from_file(file_path, module_name):
    """Load a Python module from a file path."""
    try:
        # First try direct import for modules that might be properly installed
        if module_name.startswith("api_"):
            try:
                module_path = file_path.replace(".py", "").replace("/", ".")
                return importlib.import_module(module_path)
            except ImportError:
                pass  # Fall back to loading from file
                
        # Load from file
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading module {module_name} from {file_path}: {str(e)}")
        raise

class TestServerHandler(http.server.BaseHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        # Override to provide more useful request logging
        print(f"{self.command} {self.path} - {code}")
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-API-Key, Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        self._handle_request()
        
    def do_POST(self):
        self._handle_request()
    
    def _handle_request(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Map routes based on vercel.json configuration
        if path == "/api/test":
            self._handle_file("api/direct_test.py", "api_direct_test")
        elif path == "/api/auth":
            self._handle_file("api/auth.py", "api_auth")
        # For all other paths, use index.py
        else:
            self._handle_file("api/index.py", "api_index")
    
    def _handle_file(self, file_path, module_name):
        """Handle request by loading and executing the appropriate module."""
        if os.path.exists(file_path):
            try:
                # Load the module
                module = load_module_from_file(file_path, module_name)
                
                # Create and call the handler
                handler = module.Handler(self.request, self.client_address, self.server)
                
                # Call the appropriate method based on the request method
                if self.command == 'GET':
                    handler.do_GET()
                elif self.command == 'POST':
                    handler.do_POST()
                elif self.command == 'OPTIONS':
                    handler.do_OPTIONS()
            except Exception as e:
                print(f"Error handling {self.path}: {str(e)}")
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": f"File not found: {file_path}"}
            self.wfile.write(json.dumps(error_response).encode())

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""
    pass

def run_server(port=8000):
    """Run the test server."""
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, TestServerHandler)
    print(f"Starting test server on port {port}...")
    print(f"Test the API with: curl -H 'X-API-Key: {os.environ.get('API_SECRET_KEY')}' http://localhost:{port}/api/test")
    print(f"Get a JWT token with: curl -H 'X-API-Key: {os.environ.get('API_SECRET_KEY')}' http://localhost:{port}/api/auth?user_id=test_user")
    print(f"Test text generation: curl -H 'X-API-Key: {os.environ.get('API_SECRET_KEY')}' http://localhost:{port}/generate-debug?prompt=Hello")
    httpd.serve_forever()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "API_SECRET_KEY", "JWT_SECRET"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Warning: The following required environment variables are not set: {', '.join(missing_vars)}")
        print("Make sure these are defined in your .env.local file")
    
    # Run the server
    run_server() 