from core.data import load_players_db, delete_player_from_history, load_rank_data
from core.utils import Colors, get_br_rank, get_cs_rank, print_colored
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