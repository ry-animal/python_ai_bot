"""Direct test of OpenAI API."""

from fastapi import FastAPI, HTTPException
import openai
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint."""
    env_info = {
        "VERCEL": os.environ.get("VERCEL", "Not set"),
        "OPENAI_API_KEY_SET": "Yes" if os.environ.get("OPENAI_API_KEY") else "No",
        "OPENAI_API_KEY_LENGTH": len(os.environ.get("OPENAI_API_KEY", "")) if os.environ.get("OPENAI_API_KEY") else 0,
        "ENV_KEYS": list(os.environ.keys())
    }
    return {"message": "Direct OpenAI test API", "env_info": env_info}

@app.get("/direct-openai")
async def direct_openai_test():
    """Test OpenAI API directly."""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("No OpenAI API key found in environment variables")
        return {"error": "No OpenAI API key found"}
    
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
        
        return {"result": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Error using OpenAI: {str(e)}")
        return {"error": str(e)} 