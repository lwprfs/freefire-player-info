from core.data import load_players_db, delete_player_from_history, load_rank_data, load_display_config
from core.utils import Colors, get_br_rank, get_cs_rank, print_colored, format_date
from display.player import print_section, print_info

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

def compare_players(uid1, uid2, display_config=None):
    """Compare two players with display configuration"""
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
    
    # Use display config or default
    if display_config is None:
        display_config = load_display_config()
    
    rank_data = load_rank_data()
    
    # Account Info Comparison
    if display_config.get('account_info', True):
        print_section("ACCOUNT INFO COMPARISON", Colors.CYAN)
        
        # Name comparison
        name1 = p1_acc.get('AccountName', 'N/A')
        name2 = p2_acc.get('AccountName', 'N/A')
        print_info("Name", f"{name1} → {name2}", Colors.YELLOW, Colors.GREEN if name1 != name2 else Colors.END)
        
        # Region comparison
        region1 = p1_acc.get('AccountRegion', 'N/A')
        region2 = p2_acc.get('AccountRegion', 'N/A')
        print_info("Region", f"{region1} → {region2}", Colors.YELLOW, Colors.GREEN if region1 != region2 else Colors.END)
        
        # Likes comparison
        likes1 = p1_acc.get('AccountLikes', 0)
        likes2 = p2_acc.get('AccountLikes', 0)
        likes_diff = int(likes2) - int(likes1) if likes1 != 'N/A' and likes2 != 'N/A' else 0
        color = Colors.GREEN if likes_diff > 0 else Colors.RED if likes_diff < 0 else Colors.END
        print_info("Likes", f"{likes1} → {likes2} ({'+' if likes_diff > 0 else ''}{likes_diff})", Colors.YELLOW, color)
        
        # Credit Score comparison
        credit1 = p1_data.get("CreditScoreInfo", {}).get('creditScore', 'N/A')
        credit2 = p2_data.get("CreditScoreInfo", {}).get('creditScore', 'N/A')
        print_info("Credit Score", f"{credit1} → {credit2}", Colors.YELLOW)
    
    # Rank Comparison
    if display_config.get('account_activity', True):
        print_section("RANK COMPARISON", Colors.CYAN)
        
        # Level comparison
        l1, l2 = p1_acc.get('AccountLevel', 'N/A'), p2_acc.get('AccountLevel', 'N/A')
        if l1 != 'N/A' and l2 != 'N/A':
            diff = int(l2) - int(l1)
            color = Colors.GREEN if diff > 0 else Colors.RED if diff < 0 else Colors.END
            print_info("Level", f"{l1} → {l2} ({'+' if diff > 0 else ''}{diff})", Colors.YELLOW, color)
        
        # BR comparison
        b1, b2 = p1_profile.get('BrRankPoint', 'N/A'), p2_profile.get('BrRankPoint', 'N/A')
        if b1 != 'N/A' and b2 != 'N/A':
            diff = int(b2) - int(b1)
            r1, r2 = get_br_rank(b1, rank_data), get_br_rank(b2, rank_data)
            color = Colors.GREEN if diff > 0 else Colors.RED if diff < 0 else Colors.END
            print_info("BR Rank", f"{r1} ({b1}) → {r2} ({b2}) ({'+' if diff > 0 else ''}{diff} RP)", Colors.YELLOW, color)
        
        # CS comparison
        c1, c2 = p1_profile.get('CsRankPoint', 'N/A'), p2_profile.get('CsRankPoint', 'N/A')
        if c1 != 'N/A' and c2 != 'N/A' and c1 is not None and c2 is not None:
            diff = int(c2) - int(c1) if c1 != 'N/A' and c2 != 'N/A' else 0
            r1, r2 = get_cs_rank(c1, rank_data), get_cs_rank(c2, rank_data)
            color = Colors.GREEN if diff > 0 else Colors.RED if diff < 0 else Colors.END
            print_info("CS Rank", f"{r1} ({c1}★) → {r2} ({c2}★) ({'+' if diff > 0 else ''}{diff}★)", Colors.YELLOW, color)
        
        # Account creation comparison
        created1 = format_date(p1_acc.get('AccountCreateTime', 'N/A'))
        created2 = format_date(p2_acc.get('AccountCreateTime', 'N/A'))
        print_info("Account Created", f"{created1} → {created2}", Colors.YELLOW)
        
        # Last login comparison
        login1 = format_date(p1_acc.get('AccountLastLogin', 'N/A'))
        login2 = format_date(p2_acc.get('AccountLastLogin', 'N/A'))
        print_info("Last Login", f"{login1} → {login2}", Colors.YELLOW)
    
    # Equipped Items Comparison
    if display_config.get('equipped_items', True):
        print_section("EQUIPPED ITEMS COMPARISON", Colors.CYAN)
        
        p1_equipped = p1_data.get("EquippedItemsInfo", {})
        p2_equipped = p2_data.get("EquippedItemsInfo", {})
        
        # Avatar comparison
        avatar1 = p1_equipped.get('EquippedAvatarId', 'N/A')
        avatar2 = p2_equipped.get('EquippedAvatarId', 'N/A')
        print_info("Avatar", f"{avatar1} → {avatar2}", Colors.YELLOW, Colors.GREEN if avatar1 != avatar2 else Colors.END)
        
        # Banner comparison
        banner1 = p1_equipped.get('EquippedBannerId', 'N/A')
        banner2 = p2_equipped.get('EquippedBannerId', 'N/A')
        print_info("Banner", f"{banner1} → {banner2}", Colors.YELLOW, Colors.GREEN if banner1 != banner2 else Colors.END)
        
        # BP Badges comparison
        badges1 = p1_equipped.get('EquippedBPBadges', 'N/A')
        badges2 = p2_equipped.get('EquippedBPBadges', 'N/A')
        print_info("BP Badges", f"{badges1} → {badges2}", Colors.YELLOW, Colors.GREEN if badges1 != badges2 else Colors.END)
    
    # Outfit Comparison
    if display_config.get('outfit', True):
        p1_outfit = p1_data.get("EquippedItemsInfo", {}).get('EquippedOutfit', [])
        p2_outfit = p2_data.get("EquippedItemsInfo", {}).get('EquippedOutfit', [])
        
        if p1_outfit or p2_outfit:
            print_section("OUTFIT COMPARISON", Colors.CYAN)
            max_items = max(len(p1_outfit), len(p2_outfit))
            for i in range(max_items):
                item1 = p1_outfit[i] if i < len(p1_outfit) else 'N/A'
                item2 = p2_outfit[i] if i < len(p2_outfit) else 'N/A'
                if item1 != item2:
                    print_info(f"  Slot {i+1}", f"{item1} → {item2}", Colors.YELLOW, Colors.GREEN)
    
    # Weapons Comparison
    if display_config.get('weapons', True):
        p1_weapons = p1_data.get("EquippedItemsInfo", {}).get('EquippedWeapon', [])
        p2_weapons = p2_data.get("EquippedItemsInfo", {}).get('EquippedWeapon', [])
        
        if p1_weapons or p2_weapons:
            print_section("WEAPONS COMPARISON", Colors.CYAN)
            max_items = max(len(p1_weapons), len(p2_weapons))
            for i in range(max_items):
                weapon1 = p1_weapons[i] if i < len(p1_weapons) else 'N/A'
                weapon2 = p2_weapons[i] if i < len(p2_weapons) else 'N/A'
                if weapon1 != weapon2:
                    print_info(f"  Weapon {i+1}", f"{weapon1} → {weapon2}", Colors.YELLOW, Colors.GREEN)
    
    # Pet Comparison
    if display_config.get('pet_details', True):
        p1_pet = p1_data.get("PetInfo", {})
        p2_pet = p2_data.get("PetInfo", {})
        
        if p1_pet or p2_pet:
            print_section("PET COMPARISON", Colors.CYAN)
            
            pet1_id = p1_pet.get('id', 'N/A')
            pet2_id = p2_pet.get('id', 'N/A')
            if pet1_id != pet2_id:
                print_info("Pet ID", f"{pet1_id} → {pet2_id}", Colors.YELLOW, Colors.GREEN)
            
            level1 = p1_pet.get('level', 'N/A')
            level2 = p2_pet.get('level', 'N/A')
            if level1 != level2:
                diff = int(level2) - int(level1) if level1 != 'N/A' and level2 != 'N/A' else 0
                color = Colors.GREEN if diff > 0 else Colors.RED if diff < 0 else Colors.END
                print_info("Pet Level", f"{level1} → {level2} ({'+' if diff > 0 else ''}{diff})", Colors.YELLOW, color)
    
    # Guild Comparison
    if display_config.get('guild_info', True):
        p1_guild = p1_data.get("GuildInfo", {})
        p2_guild = p2_data.get("GuildInfo", {})
        
        guild1_name = p1_guild.get('GuildName', 'N/A')
        guild2_name = p2_guild.get('GuildName', 'N/A')
        
        if guild1_name != 'N/A' or guild2_name != 'N/A':
            print_section("GUILD COMPARISON", Colors.CYAN)
            print_info("Guild Name", f"{guild1_name} → {guild2_name}", Colors.YELLOW, Colors.GREEN if guild1_name != guild2_name else Colors.END)
            
            guild1_level = p1_guild.get('GuildLevel', 'N/A')
            guild2_level = p2_guild.get('GuildLevel', 'N/A')
            if guild1_level != guild2_level:
                print_info("Guild Level", f"{guild1_level} → {guild2_level}", Colors.YELLOW, Colors.GREEN)
            
            guild1_members = p1_guild.get('GuildMember', 'N/A')
            guild2_members = p2_guild.get('GuildMember', 'N/A')
            if guild1_members != guild2_members:
                print_info("Members", f"{guild1_members} → {guild2_members}", Colors.YELLOW, Colors.GREEN)

def compare_players_menu():
    """Compare players menu with display config support"""
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
            # Load display config for comparison
            display_config = load_display_config()
            compare_players(players[choice1-1], players[choice2-1], display_config)
        else:
            print_colored("Invalid selection!", Colors.RED)
    except ValueError:
        print_colored("Please enter valid numbers!", Colors.RED)