"""OpenAI client module for text generation."""

import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self, api_key=None):
        """Initialize the OpenAI client.
        
        Args:
            api_key (str, optional): OpenAI API key. Defaults to None, in which case
                it will be read from the OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
            self.client = None
            return
        
        try:
            self.client = OpenAI(api_key=self.api_key)
        except TypeError as e:
            # Handle potential initialization issues
            logger.error(f"Error initializing OpenAI client: {e}")
            # Try with minimal parameters
            try:
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.openai.com/v1")
            except Exception as e2:
                logger.error(f"Second attempt failed: {e2}")
                self.client = None
    
    def generate_text(self, prompt, model="gpt-3.5-turbo", max_tokens=100):
        """Generate text using OpenAI's API.
        
        Args:
            prompt (str): The text prompt to generate from.
            model (str, optional): The model to use. Defaults to "gpt-3.5-turbo".
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 100.
            
        Returns:
            str: The generated text or error message.
        """
        if not self.client:
            return "Error: OpenAI client not initialized properly"
        
        try:
            logger.info(f"Generating text with model {model}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}" 