"""Test OpenAI v0 API directly."""
import os
import openai
import json

def main():
    """Run the test."""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY not set in environment")
        return
    
    try:
        # Set API key
        openai.api_key = api_key
        
        # Print version
        print(f"OpenAI version: {openai.__version__}")
        
        # Make a simple completion request
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me a short joke."}
            ],
            max_tokens=50
        )
        
        # Print response
        joke = completion.choices[0].message.content
        print(f"Joke: {joke}")
        
        # Success
        print("Test successful!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main() 