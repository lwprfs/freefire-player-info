#!/usr/bin/env python3
"""
Simple proxy server to handle CORS for the Free Fire Player Info website
Run with: python proxy_server.py
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

API_BASE = "https://api.gameskinbo.com"
CONFIG_FILE = "config.json"

def load_config():
    """Load API keys from config file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"api_keys": [], "total_requests": 0, "current_api_index": 0}

def save_config(config):
    """Save config to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.route('/proxy/ff-info/get', methods=['GET'])
def get_player():
    """Proxy for FF info endpoint"""
    uid = request.args.get('uid')
    region = request.args.get('region', 'BD')
    api_key = request.headers.get('x-api-key')
    
    if not uid:
        return jsonify({"error": "UID is required"}), 400
    
    if not api_key:
        return jsonify({"error": "API key required. Please provide x-api-key header."}), 401
    
    try:
        # Make request to the actual API
        response = requests.get(
            f"{API_BASE}/ff-info/get",
            params={"uid": uid, "region": region},
            headers={"x-api-key": api_key},
            timeout=15
        )
        
        # Return the exact response from the API
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('content-type', 'application/json')
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection error. Please check your internet connection."}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

@app.route('/proxy/api/usage', methods=['GET'])
def get_usage():
    """Proxy for API usage endpoint"""
    api_key = request.headers.get('x-api-key')
    
    if not api_key:
        return jsonify({"error": "API key required. Please provide x-api-key header."}), 401
    
    try:
        response = requests.get(
            f"{API_BASE}/api/usage",
            headers={"x-api-key": api_key},
            timeout=10
        )
        
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('content-type', 'application/json')
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy/test', methods=['GET'])
def test_proxy():
    """Test endpoint to check if proxy is running"""
    return jsonify({
        "status": "ok",
        "message": "Proxy server is running",
        "timestamp": datetime.now().isoformat(),
        "api_base": API_BASE
    })

@app.route('/proxy/keys', methods=['GET'])
def get_keys_status():
    """Get status of all API keys (for debugging)"""
    config = load_config()
    keys_status = []
    
    for i, key in enumerate(config.get('api_keys', [])):
        masked = f"{key[:8]}...{key[-4:]}"
        is_active = i == config.get('current_api_index', 0)
        
        # Try to get usage
        try:
            response = requests.get(
                f"{API_BASE}/api/usage",
                headers={"x-api-key": key},
                timeout=5
            )
            if response.status_code == 200:
                usage = response.json()
                keys_status.append({
                    "index": i,
                    "key": masked,
                    "active": is_active,
                    "usage": usage
                })
            else:
                keys_status.append({
                    "index": i,
                    "key": masked,
                    "active": is_active,
                    "error": f"HTTP {response.status_code}"
                })
        except Exception as e:
            keys_status.append({
                "index": i,
                "key": masked,
                "active": is_active,
                "error": str(e)
            })
    
    return jsonify({
        "total_keys": len(keys_status),
        "keys": keys_status
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print(" 🚀 FREE FIRE PLAYER INFO PROXY SERVER ")
    print("="*60)
    print("\nThis proxy server handles CORS and forwards requests to the GameSkinBo API.")
    print("\n📍 Running on: http://localhost:5000")
    print("📋 Endpoints:")
    print("   GET /proxy/ff-info/get?uid=UID&region=BD")
    print("   GET /proxy/api/usage")
    print("   GET /proxy/test")
    print("   GET /proxy/keys")
    print("\n" + "="*60)
    print("ℹ️  Make sure to update your HTML to use:")
    print("   http://localhost:5000/proxy/ff-info/get")
    print("   instead of https://api.gameskinbo.com/ff-info/get")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)