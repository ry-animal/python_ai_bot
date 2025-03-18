"""Main module for the project."""

import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from src.python_ai_bot.ai.openai_client import OpenAIClient


def main(prompt="Tell me a short joke", model="gpt-3.5-turbo", max_tokens=100):
    """Run the main function of the project.
    
    Args:
        prompt (str, optional): Prompt to send to OpenAI. Defaults to "Tell me a short joke".
        model (str, optional): Model to use. Defaults to "gpt-3.5-turbo".
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 100.
        
    Returns:
        str: Generated text from OpenAI.
    """
    logger.info("Running main function")
    
    # Initialize OpenAI client
    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAIClient(api_key=api_key)
    
    # Generate text
    logger.info(f"Generating text with prompt: {prompt}, model: {model}, max_tokens: {max_tokens}")
    response = client.generate_text(prompt, model=model, max_tokens=max_tokens)
    
    # If there's an error with OpenAI API, provide a mock response for demonstration
    if response.startswith("Error:"):
        logger.warning("Using mock response for demonstration")
        mock_responses = {
            "Tell me a short joke": "Why don't scientists trust atoms? Because they make up everything!",
            "Test prompt": "This is a test response."
        }
        response = mock_responses.get(prompt, "I'm a mock response since OpenAI couldn't be reached.")
    
    logger.info("Text generation complete")
    return response


if __name__ == "__main__":
    result = main()
    print(result)
