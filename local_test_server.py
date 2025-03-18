"""Local test server for Vercel functions."""
import http.server
import importlib.util
import os
import sys
from urllib.parse import urlparse

def load_module_from_file(file_path, module_name):
    """Load a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class TestServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith('/api/'):
            # Extract the endpoint name from the path
            endpoint = path.split('/')[2]
            file_path = f"api/{endpoint}.py"
            
            if os.path.exists(file_path):
                try:
                    # Load the module
                    module = load_module_from_file(file_path, f"api_{endpoint}")
                    
                    # Create and call the handler
                    handler = module.Handler(self.request, self.client_address, self.server)
                    handler.do_GET()
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(f"Error: {str(e)}".encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Endpoint {endpoint} not found".encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

def run_server(port=8000):
    """Run the test server."""
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, TestServerHandler)
    print(f"Starting test server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    # Check if OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set")
        print("You can set it with: export OPENAI_API_KEY=your_key_here")
    
    # Run the server
    run_server() 