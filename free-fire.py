import requests
import json
import os
import sys
from datetime import datetime

BASE_URL = "https://api.gameskinbo.com/ff-info/get"
CONFIG_FILE = "config.json"
PLAYERS_DB = "players_db.json"
RANK_DATA_FILE = "rank_data.json"
ASSETS_DIR = "assets"
CDN_FILE = f"{ASSETS_DIR}/cdn.json"
ITEM_DATA_FILE = f"{ASSETS_DIR}/itemData.json"

# Cache for loaded data with indexes
_cached_data = {
    'rank_data': None,
    'cdn_data': None,
    'item_data': None,
    'items_by_id': None,
    'cdn_by_id': None,
    'cdn_loaded': False
}

# Display sections configuration
DISPLAY_SECTIONS = {
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

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"api_key": None, "total_requests": 0}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_players_db():
    if os.path.exists(PLAYERS_DB):
        with open(PLAYERS_DB, 'r') as f:
            return json.load(f)
    return {}

def save_players_db(db):
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

def get_rare_color(rare):
    rare_colors = {
        'WHITE': Colors.WHITE,
        'GREEN': Colors.GREEN,
        'BLUE': Colors.BLUE,
        'PURPLE': Colors.PURPLE,
        'GOLD': Colors.GOLD,
        'RED': Colors.RED,
        'ORANGE': Colors.ORANGE
    }
    return rare_colors.get(rare, Colors.END)

def delete_player_from_history(uid):
    db = load_players_db()
    if uid in db:
        del db[uid]
        save_players_db(db)
        return True
    return False

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    PURPLE = '\033[35m'
    GOLD = '\033[33m'
    ORANGE = '\033[38;5;208m'
    WHITE = '\033[97m'
    MAGENTA = '\033[35m'

def format_date(timestamp):
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return "N/A"

def get_br_rank(points, rank_data=None):
    """Get BR rank with optional pre-loaded rank data"""
    if rank_data is None:
        rank_data = load_rank_data()
    
    br_ranks = rank_data.get("br", {})
    
    if points == "N/A" or points is None or points == "":
        return "Unranked"
    
    try:
        points = int(points)
    except:
        return "Unranked"
    
    for rank_name, rank_info in br_ranks.items():
        if rank_info["min_rp"] <= points <= rank_info["max_rp"]:
            return rank_name
    return "Unranked"

def get_cs_rank(stars, rank_data=None):
    """Get CS rank with optional pre-loaded rank data"""
    if rank_data is None:
        rank_data = load_rank_data()
    
    cs_ranks = rank_data.get("cs", {})
    
    if stars == "N/A" or stars is None or stars == "":
        return "Unranked"
    
    try:
        stars = int(stars)
    except:
        return "Unranked"
    
    for rank_name, rank_info in cs_ranks.items():
        if rank_info["min_stars"] <= stars <= rank_info["max_stars"]:
            return rank_name
    return "Unranked"

def print_colored(text, color=Colors.END, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.END}")
    else:
        print(f"{color}{text}{Colors.END}")

def print_section(title, color=Colors.CYAN):
    print_colored(f"\n{'='*50}", color)
    print_colored(f" {title}", color, bold=True)
    print_colored(f"{'='*50}", color)

def print_info(label, value, label_color=Colors.YELLOW, value_color=Colors.END):
    if value and value != "N/A" and value != "" and value != "None":
        print(f"{label_color}{label}:{Colors.END} {value_color}{value}{Colors.END}")
    else:
        print(f"{label_color}{label}:{Colors.END} {Colors.RED}N/A{Colors.END}")

def print_info_with_asset(label, value, item_id, label_color=Colors.YELLOW):
    """Print info with asset details using indexed data - O(1) lookup"""
    if value and value != "N/A" and value != "" and value != "None":
        # Load and index data once
        load_item_data()
        load_cdn_data()
        
        # O(1) lookup using indexes
        item_info = get_item_info(item_id)
        
        display_value = str(value)
        if item_info:
            if item_info['description'] and item_info['description'] != 'NONE':
                rare_color = get_rare_color(item_info['rare'])
                display_value = f"{value} ({rare_color}{item_info['description']}{Colors.END})"
        print(f"{label_color}{label}:{Colors.END} {display_value}")
    else:
        print(f"{label_color}{label}:{Colors.END} {Colors.RED}N/A{Colors.END}")

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

def show_changes(uid, old_data, new_data):
    """Show changes with cached rank data"""
    print_section("CHANGES DETECTED", Colors.GOLD)
    
    old_acc = old_data.get("AccountInfo", {})
    new_acc = new_data.get("AccountInfo", {})
    old_profile = old_data.get("AccountProfileInfo", {})
    new_profile = new_data.get("AccountProfileInfo", {})
    
    # Load rank data once for both BR and CS
    rank_data = load_rank_data()
    
    changes = []
    
    if old_acc.get('AccountName') != new_acc.get('AccountName'):
        changes.append(f"Name: {Colors.RED}{old_acc.get('AccountName')}{Colors.END} → {Colors.GREEN}{new_acc.get('AccountName')}{Colors.END}")
    
    if old_acc.get('AccountLevel') != new_acc.get('AccountLevel'):
        changes.append(f"Level: {Colors.RED}{old_acc.get('AccountLevel')}{Colors.END} → {Colors.GREEN}{new_acc.get('AccountLevel')}{Colors.END}")
    
    if old_acc.get('AccountLikes') != new_acc.get('AccountLikes'):
        changes.append(f"Likes: {Colors.RED}{old_acc.get('AccountLikes')}{Colors.END} → {Colors.GREEN}{new_acc.get('AccountLikes')}{Colors.END}")
    
    old_br = old_profile.get('BrRankPoint', 'N/A')
    new_br = new_profile.get('BrRankPoint', 'N/A')
    if old_br != new_br:
        old_rank = get_br_rank(old_br, rank_data)
        new_rank = get_br_rank(new_br, rank_data)
        changes.append(f"BR Rank: {Colors.RED}{old_rank} ({old_br}){Colors.END} → {Colors.GREEN}{new_rank} ({new_br}){Colors.END}")
    
    old_cs = old_profile.get('CsRankPoint', 'N/A')
    new_cs = new_profile.get('CsRankPoint', 'N/A')
    if old_cs != new_cs:
        old_rank = get_cs_rank(old_cs, rank_data)
        new_rank = get_cs_rank(new_cs, rank_data)
        changes.append(f"CS Rank: {Colors.RED}{old_rank} ({old_cs}★){Colors.END} → {Colors.GREEN}{new_rank} ({new_cs}★){Colors.END}")
    
    if changes:
        for change in changes:
            print_colored(f"• {change}", Colors.WHITE)
    else:
        print_colored("No changes detected in this account.", Colors.YELLOW)

def export_player_json(uid, data):
    acc = data.get("AccountInfo", {})
    player_name = acc.get('AccountName', uid).replace('/', '_').replace('\\', '_')
    filename = f"{player_name}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print_colored(f"Data exported to {filename}", Colors.GREEN)
    return filename

def compare_players(uid1, uid2):
    """Compare players with cached data"""
    db = load_players_db()
    
    if uid1 not in db or uid2 not in db:
        print_colored("One or both players not found in database!", Colors.RED)
        return
    
    player1 = db[uid1]
    player2 = db[uid2]
    
    print_section(f"COMPARING PLAYERS", Colors.GOLD)
    print_colored(f"\n{Colors.BOLD}{Colors.GREEN}{player1['name']}{Colors.END} vs {Colors.BOLD}{Colors.GREEN}{player2['name']}{Colors.END}")
    
    p1_data = player1['data']
    p2_data = player2['data']
    
    p1_acc = p1_data.get("AccountInfo", {})
    p2_acc = p2_data.get("AccountInfo", {})
    p1_profile = p1_data.get("AccountProfileInfo", {})
    p2_profile = p2_data.get("AccountProfileInfo", {})
    
    print_section("STATS COMPARISON", Colors.CYAN)
    
    p1_level = p1_acc.get('AccountLevel', 'N/A')
    p2_level = p2_acc.get('AccountLevel', 'N/A')
    level_diff = int(p2_level) - int(p1_level) if p1_level != 'N/A' and p2_level != 'N/A' else 0
    print_info(f"Level", f"{p1_level} → {p2_level} ({'+' if level_diff > 0 else ''}{level_diff})", Colors.YELLOW, Colors.GREEN if level_diff > 0 else Colors.RED if level_diff < 0 else Colors.END)
    
    p1_likes = p1_acc.get('AccountLikes', 0)
    p2_likes = p2_acc.get('AccountLikes', 0)
    likes_diff = p2_likes - p1_likes
    print_info(f"Likes", f"{p1_likes} → {p2_likes} ({'+' if likes_diff > 0 else ''}{likes_diff})", Colors.YELLOW, Colors.GREEN if likes_diff > 0 else Colors.RED if likes_diff < 0 else Colors.END)
    
    # Load rank data once for both comparisons
    rank_data = load_rank_data()
    
    p1_br = p1_profile.get('BrRankPoint', 'N/A')
    p2_br = p2_profile.get('BrRankPoint', 'N/A')
    if p1_br != 'N/A' and p2_br != 'N/A':
        br_diff = int(p2_br) - int(p1_br)
        p1_rank = get_br_rank(p1_br, rank_data)
        p2_rank = get_br_rank(p2_br, rank_data)
        print_info(f"BR Rank", f"{p1_rank} ({p1_br}) → {p2_rank} ({p2_br}) ({'+' if br_diff > 0 else ''}{br_diff} RP)", Colors.YELLOW, Colors.GREEN if br_diff > 0 else Colors.RED if br_diff < 0 else Colors.END)
    else:
        print_info("BR Rank", "N/A")
    
    p1_cs = p1_profile.get('CsRankPoint', 'N/A')
    p2_cs = p2_profile.get('CsRankPoint', 'N/A')
    if p1_cs != 'N/A' and p2_cs != 'N/A' and p1_cs is not None and p2_cs is not None:
        cs_diff = int(p2_cs) - int(p1_cs)
        p1_rank = get_cs_rank(p1_cs, rank_data)
        p2_rank = get_cs_rank(p2_cs, rank_data)
        print_info(f"CS Rank", f"{p1_rank} ({p1_cs}★) → {p2_rank} ({p2_cs}★) ({'+' if cs_diff > 0 else ''}{cs_diff}★)", Colors.YELLOW, Colors.GREEN if cs_diff > 0 else Colors.RED if cs_diff < 0 else Colors.END)
    else:
        print_info("CS Rank", "N/A")

def get_player_info(uid, region="BD", config=None, quiet=False):
    """
    Get player info with optional quiet mode for non-interactive use
    """
    if not config or not config.get("api_key"):
        if not quiet:
            print_colored("No API key found! Please set your API key first.", Colors.RED)
        return None
    
    headers = {"x-api-key": config["api_key"]}
    params = {"uid": uid, "region": region}
    
    try:
        if not quiet:
            print_colored(f"\n{Colors.BLUE}Fetching info for UID: {uid} (Region: {region}){Colors.END}")
            print_colored("Please wait...", Colors.CYAN)
        
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=15)
        
        config["total_requests"] = config.get("total_requests", 0) + 1
        save_config(config)
        
        if response.status_code == 200:
            data = response.json()
            
            db = load_players_db()
            if uid in db and not quiet:
                old_data = db[uid]['data']
                show_changes(uid, old_data, data)
            
            player_name = save_player_data(uid, data)
            
            # Display player info based on section toggles
            display_player_info(data, uid, config, quiet)
            
            if not quiet:
                print_colored("\n" + "-"*40, Colors.CYAN)
                export_choice = input(f"{Colors.YELLOW}Export player data to JSON? (y/n): {Colors.END}").strip().lower()
                if export_choice == 'y':
                    export_player_json(uid, data)
            
            return data
            
        else:
            if not quiet:
                print_colored(f"Error {response.status_code}", Colors.RED)
                print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        if not quiet:
            print_colored(f"Request failed: {e}", Colors.RED)
        return None

def display_player_info(data, uid, config, quiet=False):
    """Display player info with section toggles"""
    acc = data.get("AccountInfo", {})
    profile = data.get("AccountProfileInfo", {})
    social = data.get("SocialInfo", {})
    pet = data.get("PetInfo", {})
    guild = data.get("GuildInfo", {})
    guild_owner = data.get("GuildOwnerInfo", {})
    credit = data.get("CreditScoreInfo", {})
    equipped = data.get("EquippedItemsInfo", {})
    
    # Always show player header
    print_section("PLAYER INFO", Colors.BLUE)
    print_colored(f"\n{Colors.BOLD}{Colors.GREEN}{acc.get('AccountName', 'N/A')}{Colors.END}")
    print_colored(f"Level {acc.get('AccountLevel', 'N/A')} • {acc.get('AccountLikes', 'N/A')} Likes", Colors.CYAN)
    print_colored(f"ID opened: {format_date(acc.get('AccountCreateTime', 'N/A'))}", Colors.YELLOW)
    
    # Account Info
    if DISPLAY_SECTIONS['account_info']:
        print_section("ACCOUNT INFO", Colors.BLUE)
        print_info("UID", uid)
        print_info("Name", acc.get('AccountName', 'N/A'))
        print_info("Level", acc.get('AccountLevel', 'N/A'))
        print_info("Region", acc.get('AccountRegion', 'N/A'))
        print_info("Likes", acc.get('AccountLikes', 'N/A'))
        print_info("Season ID", acc.get('AccountSeasonId', 'N/A'))
        print_info("Credit Score", credit.get('creditScore', 'N/A'))
        
        if profile.get('Title') and profile.get('Title') != 'null':
            title_id = profile.get('Title')
            print_info_with_asset("Title", title_id, title_id)
        else:
            print_info("Title", profile.get('Title', 'N/A'))
        
        print_info("Bio", social.get('signature', 'N/A'))
        print_info("Gender", social.get('gender', 'N/A'))
        print_info("Language", social.get('language', 'N/A'))
        print_info("Time Active", social.get('timeActive', 'N/A'))
        print_info("Mode Prefer", social.get('modePrefer', 'N/A'))
        print_info("Rank Show", social.get('rankShow', 'N/A'))
    
    # Account Activity
    if DISPLAY_SECTIONS['account_activity']:
        print_section("ACCOUNT ACTIVITY", Colors.BLUE)
        print_info("Release Version", data.get('ReleaseVersion', 'N/A'))
        print_info("Account Type", data.get('AccountType', 'N/A'))
        
        # Load rank data once for both BR and CS
        rank_data = load_rank_data()
        
        br_points = profile.get('BrRankPoint', 'N/A')
        cs_stars = profile.get('CsRankPoint', 'N/A')
        
        br_rank = get_br_rank(br_points, rank_data) if br_points != 'N/A' else 'N/A'
        cs_rank = get_cs_rank(cs_stars, rank_data) if cs_stars != 'N/A' else 'N/A'
        
        print_info("BR Rank", f"{br_rank} ({br_points} RP)", value_color=Colors.GREEN)
        print_info("BR Max Rank", profile.get('BrMaxRank', 'N/A'))
        print_info("CS Rank", f"{cs_rank} ({cs_stars}★)", value_color=Colors.GREEN)
        print_info("CS Max Rank", profile.get('CsMaxRank', 'N/A'))
        
        print_info("Created At", format_date(acc.get('AccountCreateTime', 'N/A')), value_color=Colors.CYAN)
        
        last_login = format_date(acc.get('AccountLastLogin', 'N/A'))
        print_info("Last Login", last_login, value_color=Colors.RED)
    
    # Equipped Items
    if DISPLAY_SECTIONS['equipped_items']:
        print_section("EQUIPPED ITEMS", Colors.BLUE)
        
        avatar_id = equipped.get('EquippedAvatarId', 'N/A')
        if avatar_id != 'N/A' and avatar_id != 'null':
            print_info_with_asset("Avatar ID", avatar_id, avatar_id)
        else:
            print_info("Avatar ID", avatar_id)
        
        banner_id = equipped.get('EquippedBannerId', 'N/A')
        if banner_id != 'N/A' and banner_id != 'null':
            print_info_with_asset("Banner ID", banner_id, banner_id)
        else:
            print_info("Banner ID", banner_id)
        
        print_info("BP Badges", equipped.get('EquippedBPBadges', 'N/A'))
        
        bp_id = equipped.get('EquippedBPID', 'N/A')
        if bp_id != 'N/A' and bp_id != 'null':
            print_info_with_asset("BP ID", bp_id, bp_id)
        else:
            print_info("BP ID", bp_id)
        
        show_br = "Yes" if profile.get('ShowBrRank', False) else "No"
        show_cs = "Yes" if profile.get('ShowCsRank', False) else "No"
        print_info("Show BR Rank", show_br)
        print_info("Show CS Rank", show_cs)
    
    # Outfit
    if DISPLAY_SECTIONS['outfit']:
        outfit = equipped.get('EquippedOutfit', [])
        if outfit:
            print_section("OUTFIT", Colors.BLUE)
            for i, item in enumerate(outfit, 1):
                print_info_with_asset(f"  Item {i}", item, item)
    
    # Weapons
    if DISPLAY_SECTIONS['weapons']:
        weapons = equipped.get('EquippedWeapon', [])
        if weapons:
            print_section("WEAPONS", Colors.BLUE)
            for i, item in enumerate(weapons, 1):
                print_info_with_asset(f"  Weapon {i}", item, item)
    
    # Skills
    if DISPLAY_SECTIONS['skills']:
        skills = equipped.get('EquippedSkills', [])
        if skills:
            print_section("SKILLS", Colors.BLUE)
            skill_groups = [skills[i:i+4] for i in range(0, len(skills), 4)]
            for i, group in enumerate(skill_groups, 1):
                print_info(f"  Skill Slot {i}", ", ".join(str(s) for s in group))
    
    # Pet Details
    if DISPLAY_SECTIONS['pet_details']:
        if pet:
            print_section("PET DETAILS", Colors.BLUE)
            pet_id = pet.get('id', 'N/A')
            if pet_id != 'N/A' and pet_id != 'null':
                print_info_with_asset("Pet ID", pet_id, pet_id)
            else:
                print_info("Pet ID", pet_id)
            print_info("Pet Level", pet.get('level', 'N/A'))
            print_info("Pet Exp", pet.get('exp', 'N/A'))
            print_info("Pet Selected", "Yes" if pet.get('isSelected', False) else "No")
            print_info("Pet Skill ID", pet.get('selectedSkillId', 'N/A'))
            print_info("Pet Skin ID", pet.get('skinId', 'N/A'))
    
    # Guild Info
    if DISPLAY_SECTIONS['guild_info']:
        if guild and guild.get('GuildID') and guild.get('GuildID') != 'None':
            print_section("GUILD INFO", Colors.BLUE)
            print_info("Guild Name", guild.get('GuildName', 'N/A'), value_color=Colors.PURPLE)
            print_info("Guild ID", guild.get('GuildID', 'N/A'))
            print_info("Guild Level", guild.get('GuildLevel', 'N/A'))
            print_info("Guild Members", f"{guild.get('GuildMember', 'N/A')}/30")
            print_info("Guild Owner", guild.get('GuildOwner', 'N/A'))
    
    # Guild Leader
    if DISPLAY_SECTIONS['guild_leader']:
        if guild_owner:
            print_section("GUILD LEADER", Colors.BLUE)
            print_colored(f"\n{Colors.BOLD}{Colors.GREEN}{guild_owner.get('nickname', 'N/A')}{Colors.END}")
            print_info("UID", guild_owner.get('accountId', 'N/A'))
            print_info("Level", guild_owner.get('level', 'N/A'))
            print_info("Likes", guild_owner.get('liked', 'N/A'))
            print_info("BR Rank", f"{guild_owner.get('rank', 'N/A')} ({guild_owner.get('rankingPoints', 'N/A')} RP)")
            print_info("CS Rank", guild_owner.get('csRank', 'N/A'))
            print_info("Created At", format_date(guild_owner.get('createAt', 'N/A')), value_color=Colors.CYAN)
            
            leader_last_login = format_date(guild_owner.get('lastLoginAt', 'N/A'))
            print_info("Last Login", leader_last_login, value_color=Colors.RED)
    
    # API Usage
    if DISPLAY_SECTIONS['api_usage']:
        print_section("API USAGE", Colors.GOLD)
        print_info("Total API Requests", config.get("total_requests", 0))

def display_sections_menu():
    """Display and manage display sections"""
    while True:
        print_section("DISPLAY SECTIONS", Colors.GOLD)
        print_colored("\n CURRENT STATUS:", Colors.CYAN, bold=True)
        print()
        
        # Show current status
        status_map = {
            'account_info': 'Account Info',
            'account_activity': 'Account Activity',
            'equipped_items': 'Equipped Items',
            'outfit': 'Outfit',
            'weapons': 'Weapons',
            'skills': 'Skills',
            'pet_details': 'Pet Details',
            'guild_info': 'Guild Info',
            'guild_leader': 'Guild Leader',
            'api_usage': 'API Usage'
        }
        
        for key, label in status_map.items():
            status = f"[{Colors.GREEN}✓{Colors.END}]" if DISPLAY_SECTIONS[key] else f"[{Colors.RED}✗{Colors.END}]"
            print(f" {status} {label}")
        
        print_colored("\n" + "-"*50, Colors.CYAN)
        print_colored(" [a] Toggle Account Info", Colors.CYAN)
        print_colored(" [b] Toggle Account Activity", Colors.CYAN)
        print_colored(" [c] Toggle Equipped Items", Colors.CYAN)
        print_colored(" [d] Toggle Outfit", Colors.CYAN)
        print_colored(" [e] Toggle Weapons", Colors.CYAN)
        print_colored(" [f] Toggle Skills", Colors.CYAN)
        print_colored(" [g] Toggle Pet Details", Colors.CYAN)
        print_colored(" [h] Toggle Guild Info", Colors.CYAN)
        print_colored(" [i] Toggle Guild Leader", Colors.CYAN)
        print_colored(" [j] Toggle API Usage", Colors.CYAN)
        print()
        print_colored(" [x] Enable All", Colors.GREEN)
        print_colored(" [z] Disable All", Colors.RED)
        print_colored(" [0] Back to Main Menu", Colors.YELLOW)
        print_colored("-"*50, Colors.CYAN)
        
        choice = get_input(f"{Colors.YELLOW}Enter option: {Colors.END}")
        
        if choice == '0':
            break
        elif choice == 'x':
            for key in DISPLAY_SECTIONS:
                DISPLAY_SECTIONS[key] = True
            print_colored("All sections enabled!", Colors.GREEN)
        elif choice == 'z':
            for key in DISPLAY_SECTIONS:
                DISPLAY_SECTIONS[key] = False
            print_colored("All sections disabled!", Colors.RED)
        elif choice in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
            section_map = {
                'a': 'account_info',
                'b': 'account_activity',
                'c': 'equipped_items',
                'd': 'outfit',
                'e': 'weapons',
                'f': 'skills',
                'g': 'pet_details',
                'h': 'guild_info',
                'i': 'guild_leader',
                'j': 'api_usage'
            }
            key = section_map[choice]
            DISPLAY_SECTIONS[key] = not DISPLAY_SECTIONS[key]
            status = "enabled" if DISPLAY_SECTIONS[key] else "disabled"
            print_colored(f"Section toggled: {status}", Colors.GREEN if DISPLAY_SECTIONS[key] else Colors.RED)
        else:
            print_colored("Invalid option!", Colors.RED)

def view_history():
    db = load_players_db()
    if not db:
        print_colored("No players in database yet!", Colors.YELLOW)
        return
    
    print_section("PLAYER HISTORY", Colors.GOLD)
    players = list(db.items())
    
    for i, (uid, data) in enumerate(players, 1):
        print_colored(f"\n{i}. {Colors.GREEN}{data['name']}{Colors.END}")
        print_info("UID", uid)
        print_info("First Seen", data.get('first_seen', 'N/A'))
        print_info("Last Updated", data.get('last_updated', 'N/A'))
    
    print_colored("\n" + "-"*40, Colors.CYAN)
    choice = input(f"{Colors.YELLOW}Delete a player? (y/n): {Colors.END}").strip().lower()
    if choice == 'y':
        try:
            num = int(input(f"{Colors.YELLOW}Enter player number to delete: {Colors.END}"))
            if 1 <= num <= len(players):
                uid_to_delete = players[num-1][0]
                name = players[num-1][1]['name']
                confirm = input(f"{Colors.RED}Delete {name} ({uid_to_delete})? (y/n): {Colors.END}").strip().lower()
                if confirm == 'y':
                    if delete_player_from_history(uid_to_delete):
                        print_colored(f"Player {name} deleted successfully!", Colors.GREEN)
                    else:
                        print_colored("Failed to delete player!", Colors.RED)
            else:
                print_colored("Invalid number!", Colors.RED)
        except ValueError:
            print_colored("Please enter a valid number!", Colors.RED)

def compare_players_menu():
    db = load_players_db()
    if len(db) < 2:
        print_colored("Need at least 2 players in database to compare!", Colors.RED)
        return
    
    print_section("COMPARE PLAYERS", Colors.GOLD)
    players = list(db.keys())
    
    print_colored("\nAvailable players:", Colors.CYAN)
    for i, uid in enumerate(players, 1):
        print(f"{i}. {db[uid]['name']} ({uid})")
    
    try:
        choice1 = int(input(f"{Colors.YELLOW}Select first player (number): {Colors.END}"))
        choice2 = int(input(f"{Colors.YELLOW}Select second player (number): {Colors.END}"))
        
        if 1 <= choice1 <= len(players) and 1 <= choice2 <= len(players):
            compare_players(players[choice1-1], players[choice2-1])
        else:
            print_colored("Invalid selection!", Colors.RED)
    except ValueError:
        print_colored("Please enter valid numbers!", Colors.RED)

def get_input(prompt):
    user_input = input(prompt).strip()
    if user_input == '':
        return 'exit'
    return user_input

def main():
    config = load_config()
    
    # Check for non-interactive mode (UID passed as argument)
    if len(sys.argv) > 1:
        uid = sys.argv[1]
        region = sys.argv[2] if len(sys.argv) > 2 else "BD"
        
        print_colored("\n" + "="*60, Colors.CYAN)
        print_colored(" FREE FIRE PLAYER INFO ", Colors.BLUE, bold=True)
        print_colored("="*60, Colors.CYAN)
        
        if not config.get("api_key"):
            print_colored("\nNo API key found!", Colors.RED)
            sys.exit(1)
        
        # Load assets for faster display        load_item_data()
        load_cdn_data()
        load_rank_data()
        
        get_player_info(uid, region, config, quiet=False)
        sys.exit(0)
    
    # Interactive mode
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored(" FREE FIRE PLAYER INFO ", Colors.BLUE, bold=True)
    print_colored("="*60, Colors.CYAN)
    
    if not config.get("api_key"):
        print_colored("\nNo API key found!", Colors.YELLOW)
        api_key = get_input(f"{Colors.YELLOW}Enter your GamesKinbo API key (press Enter to exit): {Colors.END}")
        if api_key == 'exit':
            print_colored("\nExiting...", Colors.CYAN)
            return
        if api_key:
            config["api_key"] = api_key
            config["total_requests"] = 0
            save_config(config)
            print_colored("API key saved successfully!", Colors.GREEN)
        else:
            print_colored("API key is required to use this tool!", Colors.RED)
            return
    
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']
    
    while True:
        print_colored("\n" + "-"*40, Colors.CYAN)
        print_colored(" MAIN MENU ", Colors.CYAN, bold=True)
        print_colored("-"*40, Colors.CYAN)
        
        db = load_players_db()
        players = list(db.items())
        
        if players:
            print_colored("\n📋 RECENT PLAYERS:", Colors.GOLD)
            recent = players[-10:] if len(players) >= 10 else players
            for i, (uid, data) in enumerate(recent):
                letter = letters[i]
                print_colored(f"   [{Colors.GREEN}{letter}{Colors.END}] {Colors.GREEN}{data['name']}{Colors.END} ({uid})")
            print_colored(f"   [{Colors.CYAN}0{Colors.END}] Check New UID", Colors.CYAN)
        else:
            print_colored("\nNo players in history yet.", Colors.YELLOW)
            print_colored(f"   [{Colors.CYAN}0{Colors.END}] Check New UID", Colors.CYAN)
        
        print_colored("\n" + "─"*40, Colors.CYAN)
        print_colored(" MAIN OPTIONS:", Colors.CYAN)
        print_colored(f"   [{Colors.GREEN}1{Colors.END}] Check Player UID", Colors.GREEN)
        print_colored(f"   [{Colors.BLUE}2{Colors.END}] View History", Colors.BLUE)
        print_colored(f"   [{Colors.PURPLE}3{Colors.END}] Compare Two Players", Colors.PURPLE)
        print_colored(f"   [{Colors.YELLOW}4{Colors.END}] Change API Key", Colors.YELLOW)
        print_colored(f"   [{Colors.GOLD}5{Colors.END}] Display Sections", Colors.GOLD)
        print_colored(f"   [{Colors.RED}6{Colors.END}] Exit", Colors.RED)
        print_colored("─"*40, Colors.CYAN)
        
        print_colored("\n💡 TIP: Enter letter for recent player, '0' for new UID, or [1-5] for main options", Colors.CYAN)
        choice = get_input(f"{Colors.YELLOW}Your choice (press Enter to exit): {Colors.END}")
        
        if choice == 'exit':
            print_colored("\nGoodbye!", Colors.CYAN)
            break
        
        if choice == '0':
            uid = get_input(f"{Colors.YELLOW}Enter Free Fire UID (press Enter to cancel): {Colors.END}")
            if uid == 'exit':
                continue
            
            if not uid:
                print_colored("UID cannot be empty!", Colors.RED)
                continue
            
            region = get_input(f"{Colors.YELLOW}Region (BD/IND/BR/US/ID/SG/PK, press Enter for BD): {Colors.END}")
            if region == 'exit':
                continue
            
            if not region:
                region = "BD"
            
            # Load assets for faster display
            load_item_data()
            load_cdn_data()
            load_rank_data()
            
            get_player_info(uid, region, config)
            
        elif choice in ['1', '2', '3', '4', '5', '6']:
            if choice == '1':
                uid = get_input(f"{Colors.YELLOW}Enter Free Fire UID (press Enter to cancel): {Colors.END}")
                if uid == 'exit':
                    continue
                
                if not uid:
                    print_colored("UID cannot be empty!", Colors.RED)
                    continue
                
                region = get_input(f"{Colors.YELLOW}Region (BD/IND/BR/US/ID/SG/PK, press Enter for BD): {Colors.END}")
                if region == 'exit':
                    continue
                
                if not region:
                    region = "BD"
                
                # Load assets for faster display
                load_item_data()
                load_cdn_data()
                load_rank_data()
                
                get_player_info(uid, region, config)
                
            elif choice == '2':
                view_history()
                
            elif choice == '3':
                compare_players_menu()
                
            elif choice == '4':
                api_key = get_input(f"{Colors.YELLOW}Enter new GamesKinbo API key (press Enter to cancel): {Colors.END}")
                if api_key == 'exit':
                    continue
                
                if api_key:
                    config["api_key"] = api_key
                    save_config(config)
                    print_colored("API key updated successfully!", Colors.GREEN)
                else:
                    print_colored("API key cannot be empty!", Colors.RED)
            
            elif choice == '5':
                display_sections_menu()
                    
            elif choice == '6':
                print_colored("\nGoodbye!", Colors.CYAN)
                break
        else:
            try:
                if choice in letters:
                    idx = letters.index(choice)
                    if players and idx < len(players):
                        uid = players[idx][0]
                        region = "BD"
                        
                        # Load assets for faster display
                        load_item_data()
                        load_cdn_data()
                        load_rank_data()
                        
                        print_colored(f"\n{Colors.BLUE}Fetching info for {players[idx][1]['name']} ({uid}){Colors.END}")
                        print_colored("Please wait...", Colors.CYAN)
                        get_player_info(uid, region, config)
                    else:
                        print_colored("Invalid selection!", Colors.RED)
                else:
                    print_colored("Invalid option!", Colors.RED)
            except ValueError:
                print_colored("Invalid option!", Colors.RED)

if __name__ == "__main__":
    main()