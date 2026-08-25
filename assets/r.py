# assets/simple_update_cdn.py
import json
import os
import requests

def update_cdn_simple():
    """
    Simple script to add missing GitHub icon URLs to cdn.json
    """
    print("🔍 Checking for missing CDN entries...")
    print("=" * 50)
    
    # Load files
    with open('itemData.json', 'r') as f:
        items = json.load(f)
    
    with open('cdn.json', 'r') as f:
        cdn = json.load(f)
    
    print(f"📦 Loaded {len(items):,} items from itemData.json")
    print(f"📂 Loaded {len(cdn):,} entries from cdn.json")
    
    # Get existing IDs from CDN
    existing_ids = set()
    for entry in cdn:
        for item_id in entry.keys():
            existing_ids.add(item_id)
    
    # Find missing items
    missing = []
    for item in items:
        item_id = str(item.get('itemID', ''))
        if item_id and item_id not in existing_ids:
            missing.append(item_id)
    
    if not missing:
        print("\n✅ All items already have CDN entries!")
        return
    
    print(f"\n📝 Found {len(missing):,} items missing CDN entries")
    
    # Add missing items
    base_url = "https://raw.githubusercontent.com/ilanzera/ff-items-database-ptbr/main/assets/icons/"
    added = 0
    
    for item_id in missing:
        cdn.append({item_id: f"{base_url}{item_id}.png"})
        added += 1
        
        # Show progress every 100 items
        if added % 100 == 0:
            print(f"   Added {added}/{len(missing)} items...")
    
    # Save updated cdn.json
    with open('cdn.json', 'w') as f:
        json.dump(cdn, f, indent=4)
    
    print(f"\n✅ Added {added:,} new entries to cdn.json")
    print(f"📁 Total entries now: {len(cdn):,}")

if __name__ == "__main__":
    update_cdn_simple()