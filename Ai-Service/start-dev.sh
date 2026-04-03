#!/bin/bash

# DocMind AI Service - Development Mode
# Single worker with auto-reload for development

HOST="0.0.0.0"
PORT=8000

echo "Starting DocMind AI Service in DEVELOPMENT mode..."
echo "Auto-reload enabled - changes will restart the server"
echo "Access the service at http://$HOST:$PORT"

cd "$(dirname "$0")"

uvicorn app.main:app \
    --host $HOST \
    --port $PORT \
    --reload \
    --log-level debug
