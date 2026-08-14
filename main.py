import sys
from core.api import load_config, save_config
from core.data import load_players_db, save_player_data, load_rank_data, load_cdn_data, load_item_data
from core.utils import Colors, print_colored
from display.player import display_player_info, display_sections_menu, get_input
from compare.compare import show_changes, compare_players_menu
import requests
import json
import os

def export_player_json(uid, data):
    acc = data.get("AccountInfo", {})
    player_name = acc.get('AccountName', uid).replace('/', '_').replace('\\', '_')
    filename = f"{player_name}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print_colored(f"Data exported to {filename}", Colors.GREEN)
    return filename

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
        
        response = requests.get("https://api.gameskinbo.com/ff-info/get", headers=headers, params=params, timeout=15)
        
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

def view_history():
    db = load_players_db()
    if not db:
        print_colored("No players in database yet!", Colors.YELLOW)
        return
    
    from display.player import print_section, print_info
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
                from core.data import delete_player_from_history
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
        
        # Load assets for faster display
        load_item_data()
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