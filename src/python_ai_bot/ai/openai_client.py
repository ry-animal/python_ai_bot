"""OpenAI client module for text generation."""

import logging
import os
import time
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
        self.client = None
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
            return
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client with error handling."""
        try:
            # Basic initialization
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except TypeError as e:
            # Handle potential initialization issues with proxies
            logger.error(f"Error initializing OpenAI client: {e}")
            try:
                # Try with minimal parameters
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.openai.com/v1"
                )
                logger.info("OpenAI client initialized with minimal parameters")
            except Exception as e2:
                logger.error(f"Second initialization attempt failed: {e2}")
        except Exception as e:
            logger.error(f"Unexpected error initializing OpenAI client: {e}")
    
    def generate_text(self, prompt, model="gpt-3.5-turbo", max_tokens=100):
        """Generate text using OpenAI's API.
        
        Args:
            prompt (str): The text prompt to generate from.
            model (str, optional): The model to use. Defaults to "gpt-3.5-turbo".
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 100.
            
        Returns:
            str: The generated text or error message.
        """
        # Try to initialize client if it's not already initialized
        if not self.client and self.api_key:
            logger.info("Attempting to initialize client on demand")
            self._initialize_client()
            
        if not self.client:
            return "Error: OpenAI client not initialized properly"
        
        try:
            logger.info(f"Generating text with model {model}")
            
            # Adding retries for API stability
            max_retries = 3
            backoff_factor = 1
            
            for attempt in range(max_retries):
                try:
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
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        sleep_time = backoff_factor * (2 ** attempt)
                        logger.info(f"Retrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}" 