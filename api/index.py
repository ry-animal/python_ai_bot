"""Vercel serverless function entry point for the Python AI Bot API."""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.python_ai_bot.api import app

# This app object is used by Vercel serverless functions
app = app 