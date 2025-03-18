#!/usr/bin/env python3

"""Debug script to check environment variables and dependencies."""

import os
import sys
import json

def load_env():
    """Load environment variables from .env.local."""
    env_vars = {}
    if os.path.exists(".env.local"):
        print("Found .env.local file")
        with open(".env.local") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
                        env_vars[key] = value if not ('key' in key.lower() or 'secret' in key.lower()) else f"{'*' * (len(value) - 4)}{value[-4:]}"
                    except Exception as e:
                        print(f"Error parsing line '{line.strip()}': {e}")
    else:
        print("No .env.local file found")
    return env_vars

def check_dependencies():
    """Check if required dependencies are installed."""
    dependencies = {
        "requests": False,
        "jwt": False
    }
    
    try:
        import requests
        dependencies["requests"] = True
    except ImportError:
        pass
    
    try:
        import jwt
        dependencies["jwt"] = True
    except ImportError:
        pass
    
    return dependencies

def main():
    """Main function."""
    print("Python version:", sys.version)
    print("\nCurrent directory:", os.getcwd())
    
    print("\nLoading environment variables...")
    env_vars = load_env()
    
    print("\nEnvironment variables:")
    for key, value in env_vars.items():
        print(f"  {key}: {value}")
    
    print("\nChecking dependencies...")
    dependencies = check_dependencies()
    for dep, installed in dependencies.items():
        print(f"  {dep}: {'Installed' if installed else 'Not installed'}")
    
    if not all(dependencies.values()):
        print("\nMissing dependencies. To install them, run:")
        if not dependencies["requests"]:
            print("  pip install requests")
        if not dependencies["jwt"]:
            print("  pip install pyjwt")
    
    print("\nSystem environment variables (subset):")
    safe_keys = [k for k in os.environ.keys() if not (
        k.lower().__contains__('key') or 
        k.lower().__contains__('secret') or 
        k.lower().__contains__('pass') or 
        k.lower().__contains__('token')
    )]
    for key in sorted(safe_keys)[:20]:  # Show first 20 safe keys
        print(f"  {key}: {os.environ.get(key)}")

if __name__ == "__main__":
    main() 