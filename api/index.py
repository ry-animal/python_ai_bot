"""Vercel serverless function entry point for the Python AI Bot API."""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app from the main API module
from src.python_ai_bot.api import app

# This is used by Vercel serverless functions
app = app 