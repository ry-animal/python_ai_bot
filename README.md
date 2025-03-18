# Python AI Bot

A Python project that uses OpenAI's API for text generation, with a RESTful API interface.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/python_ai_bot.git
cd python_ai_bot

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Configuration

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Starting the API Server

```bash
# Start the server with default settings
./start_server.py

# Or with custom parameters
./start_server.py --host 127.0.0.1 --port 5000 --reload
```

The API documentation will be available at http://localhost:8000/docs (or your custom port).

## API Endpoints

The API provides the following endpoints:

- `GET /`: Welcome message
- `GET /health`: Health check endpoint
- `POST /generate`: Generate text using OpenAI's API

Example request to the `/generate` endpoint:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a poem about Python programming",
    "model": "gpt-3.5-turbo",
    "max_tokens": 150
  }'
```

## Using as a Python Module

You can also use the library programmatically:

```python
from src.python_ai_bot.main import main

# Generate text using OpenAI
result = main(
    prompt="What are the best practices for Python code?",
    model="gpt-3.5-turbo",
    max_tokens=100
)
print(result)
```

You can also use the OpenAI client directly:

```python
from src.python_ai_bot.ai.openai_client import OpenAIClient

client = OpenAIClient()
response = client.generate_text(
    prompt="Write a poem about Python programming",
    model="gpt-4",
    max_tokens=200
)
print(response)
```

## Running Tests

```bash
pytest
```

## Project Structure

```
python_ai_bot/
├── src/
│   └── python_ai_bot/
│       ├── ai/
│       │   ├── __init__.py
│       │   └── openai_client.py
│       ├── __init__.py
│       ├── main.py
│       └── api.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .venv/
├── README.md
├── requirements.txt
├── setup.py
└── start_server.py
```
