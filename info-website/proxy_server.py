#!/usr/bin/env python3
"""
Debug-friendly proxy server for Free Fire Player Info.
Run: python3 proxy_server.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import os
import traceback
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)
CORS(app)

API_BASE = "https://api.gameskinbo.com"

# Same minimal request the working CLI (main.py) sends. Do NOT spoof
# Origin/Referer: that can make the upstream reject the request.
UPSTREAM_HEADERS = {"Accept": "application/json"}

# config.json lives in the project root (shared with the CLI)
CONFIG_FILE = os.path.join(BASE_DIR, "..", "config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"api_keys": [], "total_requests": 0, "current_api_index": 0}


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_key(request_key):
    """Use the browser-supplied key, else the first key in the CLI's config.json."""
    if request_key:
        return request_key
    cfg = load_config()
    keys = cfg.get("api_keys") or []
    if not keys:
        return None
    idx = cfg.get("current_api_index", 0)
    return keys[idx if idx < len(keys) else 0]


def mask_key(key):
    if not key:
        return "<none>"
    return f"{key[:6]}...{key[-4:]}" if len(key) > 12 else "<short>"


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    if filename.startswith('proxy/'):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(BASE_DIR, filename)


@app.route('/proxy/test', methods=['GET'])
def test_proxy():
    return jsonify({
        "status": "ok",
        "message": "Proxy server is running",
        "timestamp": datetime.now().isoformat(),
        "api_base": API_BASE,
    })


@app.route('/proxy/ff-info/get', methods=['GET'])
def get_player():
    uid = request.args.get('uid')
    region = request.args.get('region', 'BD')
    api_key = get_key(request.headers.get('x-api-key'))

    print("\n" + "=" * 60)
    print(f"[REQ] /proxy/ff-info/get uid={uid} region={region} key={mask_key(api_key)}")

    if not uid:
        return jsonify({"error": "UID is required"}), 400
    if not api_key:
        return jsonify({"error": "API key required. Add one in the website or in config.json."}), 401

    upstream_url = f"{API_BASE}/ff-info/get"
    params = {"uid": uid, "region": region}
    headers = dict(UPSTREAM_HEADERS)
    headers["x-api-key"] = api_key

    print(f"[UP ] GET {upstream_url} params={params}")
    print(f"[UP ] headers sent: {list(headers.keys())}")

    try:
        r = requests.get(upstream_url, params=params, headers=headers, timeout=20)
        ctype = r.headers.get('content-type', '<none>')
        body = r.text or ''
        print(f"[UP ] status={r.status_code} content-type={ctype} len={len(body)}")
        print(f"[UP ] body[:500]={body[:500]!r}")

        # Try to parse JSON regardless of declared content-type
        try:
            parsed = r.json()
            return jsonify(parsed), r.status_code
        except Exception:
            # Not JSON — return a structured error so the browser can show it
            return jsonify({
                "error": "Upstream returned non-JSON",
                "upstream_status": r.status_code,
                "upstream_content_type": ctype,
                "upstream_body": body[:1000],
            }), 502

    except requests.exceptions.Timeout:
        print("[ERR] Upstream timeout")
        return jsonify({"error": "Upstream timeout after 20s"}), 504
    except requests.exceptions.ConnectionError as e:
        print(f"[ERR] Connection error: {e}")
        return jsonify({"error": f"Connection error: {e}"}), 503
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERR] Unhandled: {e}\n{tb}")
        return jsonify({
            "error": f"Proxy exception: {type(e).__name__}: {e}",
            "traceback": tb.splitlines()[-5:],
        }), 500


@app.route('/proxy/api/usage', methods=['GET'])
def get_usage():
    api_key = get_key(request.headers.get('x-api-key'))
    print("\n" + "=" * 60)
    print(f"[REQ] /proxy/api/usage key={mask_key(api_key)}")

    if not api_key:
        return jsonify({"error": "API key required. Add one in the website or in config.json."}), 401

    headers = dict(UPSTREAM_HEADERS)
    headers["x-api-key"] = api_key

    try:
        r = requests.get(f"{API_BASE}/api/usage", headers=headers, timeout=15)
        ctype = r.headers.get('content-type', '<none>')
        print(f"[UP ] status={r.status_code} content-type={ctype} body[:300]={r.text[:300]!r}")
        try:
            return jsonify(r.json()), r.status_code
        except Exception:
            return jsonify({
                "error": "Upstream returned non-JSON",
                "upstream_status": r.status_code,
                "upstream_content_type": ctype,
                "upstream_body": r.text[:1000],
            }), 502
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERR] {e}\n{tb}")
        return jsonify({"error": f"Proxy exception: {type(e).__name__}: {e}"}), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print(" 🚀 FREE FIRE PLAYER INFO PROXY (debug mode v2) ")
    print("=" * 60)
    print(" Running on: http://localhost:5000")
    print(" Website:    http://localhost:5000")
    print(" Test:       http://localhost:5000/proxy/test")
    print("=" * 60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)