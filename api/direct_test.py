"""Direct test of OpenAI API using Flask."""

from flask import Flask, jsonify
import openai
import os
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Root endpoint."""
    try:
        env_info = {
            "VERCEL": os.environ.get("VERCEL", "Not set"),
            "OPENAI_API_KEY_SET": "Yes" if os.environ.get("OPENAI_API_KEY") else "No",
            "OPENAI_API_KEY_LENGTH": len(os.environ.get("OPENAI_API_KEY", "")) if os.environ.get("OPENAI_API_KEY") else 0,
            "ENV_KEYS": list(os.environ.keys())
        }
        return jsonify({"message": "Direct OpenAI test API", "env_info": env_info})
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/direct-openai')
def direct_openai_test():
    """Test OpenAI API directly."""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            logger.error("No OpenAI API key found in environment variables")
            return jsonify({"error": "No OpenAI API key found"})
        
        try:
            logger.info(f"Using OpenAI API key (length: {len(api_key)})")
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Tell me a short joke"}
                ],
                max_tokens=100
            )
            
            return jsonify({"result": response.choices[0].message.content})
        except Exception as e:
            logger.error(f"Error using OpenAI: {str(e)}")
            return jsonify({"error": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"critical_error": str(e)})

# Vercel handler
def handler(request):
    """Handle Vercel serverless function requests."""
    return app(request) 