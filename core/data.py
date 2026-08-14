import json
import os
from datetime import datetime

PLAYERS_DB = "data/players_db.json"
RANK_DATA_FILE = "data/rank_data.json"
ASSETS_DIR = "assets"
CDN_FILE = f"{ASSETS_DIR}/cdn.json"
ITEM_DATA_FILE = f"{ASSETS_DIR}/itemData.json"
DISPLAY_CONFIG_FILE = "display/display_config.json"

# Cache for loaded data with indexes
_cached_data = {
    'rank_data': None,
    'cdn_data': None,
    'item_data': None,
    'items_by_id': None,
    'cdn_by_id': None,
    'cdn_loaded': False
}

def load_display_config():
    """Load display section configuration"""
    if os.path.exists(DISPLAY_CONFIG_FILE):
        with open(DISPLAY_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'account_info': True,
        'account_activity': True,
        'equipped_items': True,
        'outfit': True,
        'weapons': True,
        'skills': True,
        'pet_details': True,
        'guild_info': True,
        'guild_leader': True,
        'api_usage': True
    }

def save_display_config(config):
    with open(DISPLAY_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_players_db():
    if os.path.exists(PLAYERS_DB):
        with open(PLAYERS_DB, 'r') as f:
            return json.load(f)
    return {}

def save_players_db(db):
    os.makedirs("data", exist_ok=True)
    with open(PLAYERS_DB, 'w') as f:
        json.dump(db, f, indent=2)

def load_rank_data(force_reload=False):
    """Load rank data with caching"""
    if _cached_data['rank_data'] is None or force_reload:
        if os.path.exists(RANK_DATA_FILE):
            with open(RANK_DATA_FILE, 'r') as f:
                _cached_data['rank_data'] = json.load(f)
        else:
            _cached_data['rank_data'] = {"br": {}, "cs": {}}
    return _cached_data['rank_data']

def load_cdn_data(force_reload=False):
    """Load CDN data with caching and indexing"""
    if not _cached_data['cdn_loaded'] or force_reload:
        if os.path.exists(CDN_FILE):
            with open(CDN_FILE, 'r') as f:
                _cached_data['cdn_data'] = json.load(f)
        else:
            _cached_data['cdn_data'] = []
        
        # Build CDN index for O(1) lookups
        _cached_data['cdn_by_id'] = {}
        for cdn_entry in _cached_data['cdn_data']:
            for item_id, url in cdn_entry.items():
                _cached_data['cdn_by_id'][item_id] = url
        
        _cached_data['cdn_loaded'] = True
    
    return _cached_data['cdn_data']

def load_item_data(force_reload=False):
    """Load item data with caching and indexing"""
    if _cached_data['item_data'] is None or force_reload:
        if os.path.exists(ITEM_DATA_FILE):
            with open(ITEM_DATA_FILE, 'r') as f:
                _cached_data['item_data'] = json.load(f)
        else:
            _cached_data['item_data'] = []
        
        # Build item index for O(1) lookups
        _cached_data['items_by_id'] = {}
        for item in _cached_data['item_data']:
            item_id = str(item.get('itemID'))
            if item_id:
                _cached_data['items_by_id'][item_id] = item
    
    return _cached_data['item_data']

def get_item_info(item_id, item_data=None, cdn_data=None):
    """Get item info using indexed lookups - O(1) instead of O(n)"""
    item_id_str = str(item_id)
    
    # Ensure indexes are built
    if item_data is None:
        load_item_data()
    if cdn_data is None:
        load_cdn_data()
    
    # O(1) lookup using index
    item = _cached_data['items_by_id'].get(item_id_str)
    
    if item:
        description = item.get('description', '')
        rare = item.get('Rare', 'NONE')
        item_type = item.get('itemType', '')
        
        # O(1) CDN lookup using index
        cdn_url = _cached_data['cdn_by_id'].get(item_id_str)
        
        return {
            'description': description,
            'rare': rare,
            'item_type': item_type,
            'cdn_url': cdn_url
        }
    return None

def save_player_data(uid, data):
    db = load_players_db()
    acc = data.get("AccountInfo", {})
    player_name = acc.get('AccountName', uid)
    
    if uid in db:
        old_data = db[uid]
        db[uid] = {
            "uid": uid,
            "name": player_name,
            "data": data,
            "last_updated": datetime.now().isoformat(),
            "first_seen": old_data.get("first_seen", datetime.now().isoformat())
        }
    else:
        db[uid] = {
            "uid": uid,
            "name": player_name,
            "data": data,
            "last_updated": datetime.now().isoformat(),
            "first_seen": datetime.now().isoformat()
        }
    save_players_db(db)
    return player_name

def delete_player_from_history(uid):
    db = load_players_db()
    if uid in db:
        del db[uid]
        save_players_db(db)
        return True
    return False