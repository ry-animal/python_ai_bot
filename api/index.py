"""Vercel serverless function entry point for the Python AI Bot API."""

import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Log environment variables for debugging (excluding sensitive values)
logger.info("Vercel environment: %s", os.environ.get("VERCEL", "Not set"))
logger.info("Environment variables set: %s", list(filter(lambda k: not k.startswith("OPENAI_"), os.environ.keys())))
logger.info("OPENAI_API_KEY set: %s", "Yes" if os.environ.get("OPENAI_API_KEY") else "No")

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from ai module to reduce import complexity
from src.python_ai_bot.api import app

# This is used by Vercel serverless functions
app = app 