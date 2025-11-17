#!/bin/bash

echo "🌽 Starting AgriCom Pest Prediction Web Application..."
echo "=================================================="
echo ""
echo "Server will be available at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
