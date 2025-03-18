"""API server module for the project."""

import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from src.python_ai_bot.main import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Python AI Bot API",
    description="API for generating text using OpenAI",
    version="0.1.0",
)


class PromptRequest(BaseModel):
    """Request model for the text generation endpoint."""
    
    prompt: str
    max_tokens: Optional[int] = 100
    model: Optional[str] = "gpt-3.5-turbo"


class TextResponse(BaseModel):
    """Response model for the text generation endpoint."""
    
    text: str


@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {"message": "Welcome to the Python AI Bot API"}


@app.post("/generate", response_model=TextResponse)
async def generate_text(request: PromptRequest):
    """Generate text using OpenAI's API.
    
    Args:
        request: The request containing the prompt and generation parameters.
        
    Returns:
        A response containing the generated text.
    """
    try:
        logger.info(f"Received prompt: {request.prompt}")
        result = main(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens
        )
        return TextResponse(text=result)
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating text: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.python_ai_bot.api:app", host="0.0.0.0", port=8000, reload=True) 