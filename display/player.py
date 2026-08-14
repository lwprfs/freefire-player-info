from core.utils import Colors, format_date, get_br_rank, get_cs_rank, get_rare_color, print_colored
from core.data import load_rank_data, load_item_data, load_cdn_data, get_item_info, load_display_config, save_display_config

# Load display sections from config
DISPLAY_SECTIONS = load_display_config()

def save_current_display_config():
    """Save current display section configuration"""
    save_display_config(DISPLAY_SECTIONS)

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

def display_player_info(data, uid, config, quiet=False, display_config=None):
    """Display player info with section toggles"""
    if display_config:
        global DISPLAY_SECTIONS
        DISPLAY_SECTIONS = display_config
    
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
    
    # Show active API key info
    if DISPLAY_SECTIONS.get('api_usage', True):
        active_key = config.get("api_keys", [])[config.get("current_api_index", 0)] if config.get("api_keys") else "None"
        if active_key != "None" and len(active_key) > 12:
            print_colored(f"Active API Key: {Colors.GREEN}{active_key[:8]}...{active_key[-4:]}{Colors.END}", Colors.CYAN)
        elif active_key != "None":
            print_colored(f"Active API Key: {Colors.GREEN}{active_key}{Colors.END}", Colors.CYAN)
    
    # Account Info
    if DISPLAY_SECTIONS.get('account_info', True):
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
    if DISPLAY_SECTIONS.get('account_activity', True):
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
    if DISPLAY_SECTIONS.get('equipped_items', True):
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
    if DISPLAY_SECTIONS.get('outfit', True):
        outfit = equipped.get('EquippedOutfit', [])
        if outfit:
            print_section("OUTFIT", Colors.BLUE)
            for i, item in enumerate(outfit, 1):
                print_info_with_asset(f"  Item {i}", item, item)
    
    # Weapons
    if DISPLAY_SECTIONS.get('weapons', True):
        weapons = equipped.get('EquippedWeapon', [])
        if weapons:
            print_section("WEAPONS", Colors.BLUE)
            for i, item in enumerate(weapons, 1):
                print_info_with_asset(f"  Weapon {i}", item, item)
    
    # Skills
    if DISPLAY_SECTIONS.get('skills', True):
        skills = equipped.get('EquippedSkills', [])
        if skills:
            print_section("SKILLS", Colors.BLUE)
            skill_groups = [skills[i:i+4] for i in range(0, len(skills), 4)]
            for i, group in enumerate(skill_groups, 1):
                print_info(f"  Skill Slot {i}", ", ".join(str(s) for s in group))
    
    # Pet Details
    if DISPLAY_SECTIONS.get('pet_details', True):
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
    if DISPLAY_SECTIONS.get('guild_info', True):
        if guild and guild.get('GuildID') and guild.get('GuildID') != 'None':
            print_section("GUILD INFO", Colors.BLUE)
            print_info("Guild Name", guild.get('GuildName', 'N/A'), value_color=Colors.PURPLE)
            print_info("Guild ID", guild.get('GuildID', 'N/A'))
            print_info("Guild Level", guild.get('GuildLevel', 'N/A'))
            print_info("Guild Members", f"{guild.get('GuildMember', 'N/A')}/30")
            print_info("Guild Owner", guild.get('GuildOwner', 'N/A'))
    
    # Guild Leader
    if DISPLAY_SECTIONS.get('guild_leader', True):
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
    if DISPLAY_SECTIONS.get('api_usage', True):
        print_section("API USAGE", Colors.GOLD)
        print_info("Total API Requests", config.get("total_requests", 0))
    
    # Save the config if changed
    save_current_display_config()

def display_sections_menu():
    """Display and manage display sections with persistence"""
    global DISPLAY_SECTIONS
    
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
            status = f"[{Colors.GREEN}✓{Colors.END}]" if DISPLAY_SECTIONS.get(key, True) else f"[{Colors.RED}✗{Colors.END}]"
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
            save_current_display_config()
            break
        elif choice == 'x':
            for key in DISPLAY_SECTIONS:
                DISPLAY_SECTIONS[key] = True
            save_current_display_config()
            print_colored("All sections enabled and saved!", Colors.GREEN)
        elif choice == 'z':
            for key in DISPLAY_SECTIONS:
                DISPLAY_SECTIONS[key] = False
            save_current_display_config()
            print_colored("All sections disabled and saved!", Colors.RED)
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
            DISPLAY_SECTIONS[key] = not DISPLAY_SECTIONS.get(key, True)
            save_current_display_config()
            status = "enabled" if DISPLAY_SECTIONS[key] else "disabled"
            print_colored(f"Section toggled: {status} (saved)", Colors.GREEN if DISPLAY_SECTIONS[key] else Colors.RED)
        else:
            print_colored("Invalid option!", Colors.RED)

def get_input(prompt):
    user_input = input(prompt).strip()
    if user_input == '':
        return 'exit'
    return user_input