#!/bin/bash

echo "Starting Build-a-RIG in Development Mode (No OpenAI API calls)"
echo

# Set development mode to avoid OpenAI API costs
export DEVELOPMENT_MODE=true

# Start API server in background
echo "Starting API server..."
uvicorn api.index:app --reload &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start Streamlit UI
echo "Starting Streamlit UI..."
streamlit run ui/app.py

# Clean up: kill API server when Streamlit stops
kill $API_PID 2>/dev/null 