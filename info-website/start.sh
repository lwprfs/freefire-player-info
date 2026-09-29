#!/bin/bash
echo "======================================"
echo "🚀 Starting Free Fire Player Info"
echo "======================================"
echo ""
echo "1. Starting Python proxy server..."
python3 proxy_server.py &
PROXY_PID=$!
echo "   Proxy PID: $PROXY_PID"
echo ""
echo "2. Starting HTTP server for website..."
python3 -m http.server 8081 &
HTTP_PID=$!
echo "   HTTP PID: $HTTP_PID"
echo ""
echo "======================================"
echo "📍 Website: http://localhost:8081"
echo "📍 Proxy:   http://localhost:5000"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to press Ctrl+C
trap "kill $PROXY_PID $HTTP_PID 2>/dev/null; exit" INT
wait
