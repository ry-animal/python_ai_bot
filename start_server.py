#!/usr/bin/env python
"""Script to start the API server."""

import uvicorn
import os
import argparse

def main():
    """Start the API server."""
    parser = argparse.ArgumentParser(description="Start the Python AI Bot API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    
    args = parser.parse_args()
    
    print(f"Starting Python AI Bot API server on {args.host}:{args.port}")
    print("API documentation will be available at http://localhost:8000/docs")
    
    uvicorn.run(
        "src.python_ai_bot.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main() 