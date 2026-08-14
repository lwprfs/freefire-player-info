__all__ = [
    'load_config', 'save_config', 'get_active_api_key', 'add_api_key',
    'remove_api_key', 'check_and_update_usage', 'get_cached_usage',
    'get_all_cached_usage', 'refresh_all_keys_usage', 'switch_api_key'
]
import requests
import json
import os
from datetime import datetime, date

BASE_URL = "https://api.gameskinbo.com"
CONFIG_FILE = "config.json"
USAGE_CACHE_FILE = "core/usage_cache.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"api_keys": [], "total_requests": 0, "current_api_index": 0}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_usage_cache():
    os.makedirs("core", exist_ok=True)
    if os.path.exists(USAGE_CACHE_FILE):
        with open(USAGE_CACHE_FILE, 'r') as f:
            return json.load(f)
    return {"last_check": None, "usage_data": {}, "month": None}

def save_usage_cache(cache):
    os.makedirs("core", exist_ok=True)
    with open(USAGE_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_api_usage(api_key):
    """Get usage info for a specific API key"""
    headers = {"x-api-key": api_key}
    try:
        response = requests.get(f"{BASE_URL}/api/usage", headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"error": "API key required. Please provide x-api-key header."}
        elif response.status_code == 429:
            return {"error": "Rate limit exceeded. Please slow down your requests."}
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}

def refresh_all_keys_usage(config):
    """Refresh usage for all API keys"""
    if not config.get("api_keys"):
        return {}
    
    cache = load_usage_cache()
    current_month = date.today().replace(day=1).isoformat()
    results = {}
    
    for api_key in config["api_keys"]:
        usage_data = get_api_usage(api_key)
        if usage_data and "error" not in usage_data:
            cache["month"] = current_month
            cache["last_check"] = current_month
            cache["usage_data"][api_key] = usage_data
            results[api_key] = usage_data
        else:
            results[api_key] = usage_data
    
    save_usage_cache(cache)
    return results

def check_and_update_usage(config, force=False, api_key=None):
    """
    Check usage for a specific API key or current key.
    Only makes API call once per month per key unless forced.
    """
    if not config.get("api_keys"):
        return None
    
    # Load usage cache
    cache = load_usage_cache()
    current_month = date.today().replace(day=1).isoformat()
    
    # If specific key provided, use it
    if api_key:
        target_key = api_key
    else:
        # Get current API key
        current_idx = config.get("current_api_index", 0)
        if current_idx >= len(config["api_keys"]):
            current_idx = 0
            config["current_api_index"] = 0
            save_config(config)
        target_key = config["api_keys"][current_idx]
    
    # If month changed, clear old cache
    if cache.get("month") != current_month:
        cache["month"] = current_month
        cache["usage_data"] = {}
        cache["last_check"] = None
        save_usage_cache(cache)
    
    # Check if we need to fetch new data
    if force or target_key not in cache.get("usage_data", {}) or cache.get("last_check") != current_month:
        # Fetch fresh usage data
        new_usage = get_api_usage(target_key)
        
        if new_usage and "error" not in new_usage:
            # Store in cache
            cache["last_check"] = current_month
            cache["month"] = current_month
            cache["usage_data"][target_key] = new_usage
            save_usage_cache(cache)
            
            # Update total_requests with actual used count
            config["total_requests"] = new_usage.get("used", 0)
            save_config(config)
            
            return new_usage
        elif new_usage and "error" in new_usage:
            return new_usage
    
    # Return cached usage data if available
    if target_key in cache.get("usage_data", {}):
        return cache["usage_data"][target_key]
    
    return None

def get_next_available_api_key(config):
    """Find the next API key with available requests"""
    if not config.get("api_keys"):
        return None, None
    
    # Check usage for each key
    cache = load_usage_cache()
    current_month = date.today().replace(day=1).isoformat()
    
    for idx, api_key in enumerate(config["api_keys"]):
        # Check if we have cached data for this key this month
        cached_month = cache.get("month")
        usage_data = cache.get("usage_data", {})
        
        if cached_month != current_month or api_key not in usage_data:
            # Fetch fresh usage data
            fresh_usage = get_api_usage(api_key)
            if fresh_usage and "error" not in fresh_usage:
                cache["month"] = current_month
                cache["last_check"] = current_month
                cache["usage_data"][api_key] = fresh_usage
                save_usage_cache(cache)
                usage_data = fresh_usage
            else:
                # Skip this key if we can't get usage
                continue
        else:
            usage_data = cache["usage_data"].get(api_key, {})
        
        # Check if this key has remaining requests
        remaining = usage_data.get("remaining", 0)
        if remaining > 0:
            config["current_api_index"] = idx
            save_config(config)
            return api_key, usage_data
    
    return None, None

def add_api_key(config, new_key):
    """Add a new API key to the configuration"""
    if new_key not in config["api_keys"]:
        config["api_keys"].append(new_key)
        save_config(config)
        
        # Immediately fetch usage for the new key
        check_and_update_usage(config, force=True, api_key=new_key)
        return True
    return False

def remove_api_key(config, index):
    """Remove an API key from the configuration"""
    if 0 <= index < len(config["api_keys"]):
        removed = config["api_keys"].pop(index)
        if config["current_api_index"] >= len(config["api_keys"]):
            config["current_api_index"] = 0
        save_config(config)
        return removed
    return None

def switch_api_key(config, index):
    """Switch to a different API key"""
    if 0 <= index < len(config["api_keys"]):
        config["current_api_index"] = index
        save_config(config)
        return True
    return False

def get_active_api_key(config):
    """Get the currently active API key with usage info"""
    if not config.get("api_keys"):
        return None, None
    
    # Try to get next available key
    api_key, usage = get_next_available_api_key(config)
    
    if api_key:
        return api_key, usage
    
    # No keys with remaining requests
    return None, None

def get_cached_usage(config, api_key=None):
    """Get cached usage data without making API calls"""
    if not config.get("api_keys"):
        return None
    
    cache = load_usage_cache()
    current_month = date.today().replace(day=1).isoformat()
    
    # If specific key provided, use it
    if api_key:
        target_key = api_key
    else:
        # Get current API key
        current_idx = config.get("current_api_index", 0)
        if current_idx >= len(config["api_keys"]):
            current_idx = 0
            config["current_api_index"] = 0
            save_config(config)
        target_key = config["api_keys"][current_idx]
    
    # Check if we have cached data for this month
    if cache.get("month") == current_month and target_key in cache.get("usage_data", {}):
        return cache["usage_data"][target_key]
    
    return None

def get_all_cached_usage(config):
    """Get cached usage for all keys without making API calls"""
    if not config.get("api_keys"):
        return {}
    
    cache = load_usage_cache()
    current_month = date.today().replace(day=1).isoformat()
    
    # If month changed, cache is invalid
    if cache.get("month") != current_month:
        return {}
    
    return cache.get("usage_data", {})