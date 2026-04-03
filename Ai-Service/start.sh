#!/bin/bash

# DocMind AI Service - Optimized Startup Script
# Using multiple uvicorn workers for parallel request handling

# Calculate optimal worker count: (2 * CPU_cores) + 1
# For 16 cores: (2 * 16) + 1 = 33 workers
# But we'll use a more conservative 8 workers to balance memory usage

WORKERS=8
HOST="0.0.0.0"
PORT=8000

echo "Starting DocMind AI Service with $WORKERS workers..."
echo "Access the service at http://$HOST:$PORT"

cd "$(dirname "$0")"

uvicorn app.main:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --loop uvloop \
    --timeout-keep-alive 60 \
    --log-level info
