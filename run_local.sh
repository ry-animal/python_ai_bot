#!/bin/bash

# Script to run local tests for the Python AI Bot

# Stop any existing server on port 8000
echo "Stopping any existing servers on port 8000..."
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null || true

# Load environment variables from .env.local
echo "Loading environment variables from .env.local..."
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
    
    # Check if required variables are set
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "Warning: OPENAI_API_KEY is not set in .env.local"
    else
        echo "✓ OPENAI_API_KEY is set"
    fi
    
    if [ -z "$API_SECRET_KEY" ]; then
        echo "Warning: API_SECRET_KEY is not set in .env.local"
    else
        echo "✓ API_SECRET_KEY is set"
    fi
    
    if [ -z "$JWT_SECRET" ]; then
        echo "Warning: JWT_SECRET is not set in .env.local"
    else
        echo "✓ JWT_SECRET is set"
    fi
else
    echo "Error: .env.local file not found!"
    echo "Creating a sample .env.local file..."
    cat > .env.local << EOL
OPENAI_API_KEY=your_openai_api_key_here
API_SECRET_KEY=your_api_secret_key_here
JWT_SECRET=your_jwt_secret_key_here
ALLOWED_ORIGINS=*
EOL
    echo "Please edit .env.local with your actual API keys, then run this script again."
    exit 1
fi

# Function to show menu
show_menu() {
    echo ""
    echo "Python AI Bot - Local Testing"
    echo "============================"
    echo "1) Test OpenAI API directly"
    echo "2) Try to start local HTTP server"
    echo "3) Test production API (Vercel)"
    echo "4) Deploy to Vercel"
    echo "q) Quit"
    echo ""
    echo -n "Choose an option: "
}

# Function to test OpenAI API
test_openai_api() {
    echo "Testing OpenAI API directly..."
    python test_openai_direct.py
}

# Function to start local server
start_local_server() {
    echo "Starting simplified HTTP server..."
    echo "This is a reliable alternative to the standard server."
    echo "Press Ctrl+C to stop the server."
    echo ""
    python simple_test.py
}

# Function to test production API
test_production_api() {
    echo "Testing the production API on Vercel..."
    echo ""
    
    echo "1) Testing /api/test endpoint..."
    curl -s -H "X-API-Key: $API_SECRET_KEY" "https://python-ai-bot.vercel.app/api/test" | json_pp
    echo ""
    
    echo "2) Testing /generate-debug endpoint..."
    curl -s -H "X-API-Key: $API_SECRET_KEY" "https://python-ai-bot.vercel.app/generate-debug?prompt=Tell%20me%20a%20short%20joke" | json_pp
    echo ""
    
    echo "3) Testing /api/auth endpoint..."
    curl -s -H "X-API-Key: $API_SECRET_KEY" "https://python-ai-bot.vercel.app/api/auth?user_id=test_user" | json_pp
    echo ""
}

# Function to deploy to Vercel
deploy_to_vercel() {
    echo "Deploying to Vercel..."
    vercel --prod
}

# Main loop
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) test_openai_api ;;
        2) start_local_server ;;
        3) test_production_api ;;
        4) deploy_to_vercel ;;
        q|Q) echo "Goodbye!"; exit 0 ;;
        *) echo "Invalid option. Please try again." ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read -r
done 