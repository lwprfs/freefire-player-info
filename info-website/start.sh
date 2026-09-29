#!/bin/bash

echo "======================================"
echo "🚀 Starting Free Fire Player Info"
echo "======================================"
echo ""

# --- Sanity check: python3 exists ---
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ python3 not found in PATH"
    exit 1
fi

# --- Check Python deps are installed ---
if ! python3 -c "import flask, flask_cors, requests" 2>/dev/null; then
    echo "❌ Missing Python dependencies."
    echo "   Run: pip install -r requirements.txt"
    exit 1
fi

# --- Free ports 5000 and 8090 if busy ---
for PORT in 5000 8090; do
    PIDS=$(lsof -ti tcp:$PORT 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "⚠️  Port $PORT busy — killing PID(s): $PIDS"
        kill -9 $PIDS 2>/dev/null
        sleep 1
    fi
done

# --- Start proxy ---
echo "1. Starting Python proxy server (Flask) on :5000..."
python3 proxy_server.py &
PROXY_PID=$!
echo "   Proxy PID: $PROXY_PID"

# Wait for proxy to come up (max ~10s)
UP=0
for i in $(seq 1 20); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/proxy/test 2>/dev/null | grep -q 200; then
        UP=1
        break
    fi
    sleep 0.5
done

if [ "$UP" -ne 1 ]; then
    echo "   ❌ Proxy failed to start. Check the log above."
    kill $PROXY_PID 2>/dev/null
    exit 1
fi
echo "   ✅ Proxy is up"
echo ""

# --- Start static HTTP server ---
echo "2. Starting HTTP server for website on :8090..."
python3 -m http.server 8090 &
HTTP_PID=$!
echo "   HTTP PID: $HTTP_PID"
echo ""

echo "======================================"
echo "📍 Website: http://localhost:8090"
echo "📍 Proxy:   http://localhost:5000"
echo "📍 Test:    http://localhost:5000/proxy/test"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# --- Cleanup on Ctrl+C ---
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $PROXY_PID $HTTP_PID 2>/dev/null
    wait $PROXY_PID $HTTP_PID 2>/dev/null
    echo "✅ Stopped."
    exit 0
}
trap cleanup INT TERM

wait