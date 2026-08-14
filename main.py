import sys
from core.api import (
    load_config, 
    save_config, 
    get_active_api_key, 
    add_api_key, 
    remove_api_key, 
    check_and_update_usage, 
    get_cached_usage,
    get_all_cached_usage, 
    refresh_all_keys_usage, 
    switch_api_key
)
from core.data import (
    load_players_db, 
    save_player_data, 
    load_rank_data, 
    load_cdn_data, 
    load_item_data, 
    load_display_config, 
    save_display_config
)
from core.utils import Colors, print_colored
from display.player import display_player_info, display_sections_menu, get_input, DISPLAY_SECTIONS, print_section, print_info
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
    if not config or not config.get("api_keys"):
        if not quiet:
            print_colored("No API keys found! Please add an API key first.", Colors.RED)
        return None
    
    # Get active API key with remaining requests
    api_key, usage = get_active_api_key(config)
    
    if not api_key:
        if not quiet:
            print_colored("All API keys have reached their request limits!", Colors.RED)
            print_colored("Please add more API keys or wait for the next billing cycle.", Colors.YELLOW)
        return None
    
    headers = {"x-api-key": api_key}
    params = {"uid": uid, "region": region}
    
    try:
        if not quiet:
            print_colored(f"\n{Colors.BLUE}Fetching info for UID: {uid} (Region: {region}){Colors.END}")
            print_colored(f"Using API Key: {Colors.GREEN}{api_key[:8]}...{api_key[-4:]}{Colors.END}")
            if usage and "remaining" in usage:
                print_colored(f"Remaining requests: {Colors.YELLOW}{usage.get('remaining', 0)}{Colors.END}")
            print_colored("Please wait...", Colors.CYAN)
        
        response = requests.get("https://api.gameskinbo.com/ff-info/get", headers=headers, params=params, timeout=15)
        
        # Handle different error responses
        if response.status_code == 401:
            print_colored("Error: API key required. Please provide x-api-key header.", Colors.RED)
            return None
        elif response.status_code == 429:
            try:
                error_data = response.json()
                if "API limit exceeded" in error_data.get("error", ""):
                    print_colored(f"Error: API limit exceeded. Used: {error_data.get('used', 0)}/{error_data.get('limit', 0)}", Colors.RED)
                    print_colored("Please upgrade your plan or use a different API key.", Colors.YELLOW)
                else:
                    print_colored("Error: Rate limit exceeded. Please slow down your requests.", Colors.RED)
            except:
                print_colored("Error: Rate limit exceeded. Please slow down your requests.", Colors.RED)
            return None
        elif response.status_code == 402:
            print_colored("Error: Invalid UID or server error. Please try again.", Colors.RED)
            return None
        elif response.status_code != 200:
            print_colored(f"Error {response.status_code}: {response.text}", Colors.RED)
            return None
        
        # Success - process the data
        data = response.json()
        
        # Update usage cache after successful request (force update to get latest)
        check_and_update_usage(config, force=True)
        
        db = load_players_db()
        if uid in db and not quiet:
            old_data = db[uid]['data']
            show_changes(uid, old_data, data)
        
        player_name = save_player_data(uid, data)
        
        # Load display configuration
        display_config = load_display_config()
        
        # Display player info based on section toggles
        display_player_info(data, uid, config, quiet, display_config)
        
        if not quiet:
            print_colored("\n" + "-"*40, Colors.CYAN)
            export_choice = input(f"{Colors.YELLOW}Export player data to JSON? (y/n): {Colors.END}").strip().lower()
            if export_choice == 'y':
                export_player_json(uid, data)
        
        return data
            
    except requests.exceptions.RequestException as e:
        if not quiet:
            print_colored(f"Request failed: {e}", Colors.RED)
        return None

def manage_api_keys(config):
    """Manage API keys menu"""
    while True:
        print_section("MANAGE API KEYS", Colors.GOLD)
        
        # Show current keys
        print_colored("\nCurrent API Keys:", Colors.CYAN)
        if config.get("api_keys"):
            # Get all cached usage
            all_usage = get_all_cached_usage(config)
            
            for i, key in enumerate(config["api_keys"]):
                active = " (ACTIVE)" if i == config.get("current_api_index", 0) else ""
                
                # Get usage for this specific key
                usage = all_usage.get(key)
                if usage and "error" not in usage:
                    print_colored(f"  [{i}] {Colors.GREEN}{key[:8]}...{key[-4:]}{Colors.END}{active} - {Colors.YELLOW}{usage.get('remaining', 0)}/{usage.get('limit', 0)} remaining{Colors.END}")
                elif usage and "error" in usage:
                    print_colored(f"  [{i}] {Colors.GREEN}{key[:8]}...{key[-4:]}{Colors.END}{active} - {Colors.RED}{usage.get('error')}{Colors.END}")
                else:
                    print_colored(f"  [{i}] {Colors.GREEN}{key[:8]}...{key[-4:]}{Colors.END}{active} - {Colors.RED}Usage unknown (press 'c' to refresh){Colors.END}")
        else:
            print_colored("  No API keys added yet!", Colors.RED)
        
        print_colored("\nOptions:", Colors.CYAN)
        print_colored("  [a] Add API Key", Colors.GREEN)
        print_colored("  [r] Remove API Key", Colors.RED)
        print_colored("  [s] Switch Active Key", Colors.BLUE)
        print_colored("  [c] Check Usage (refresh all)", Colors.MAGENTA)
        print_colored("  [0] Back to Main Menu", Colors.YELLOW)
        
        choice = get_input(f"{Colors.YELLOW}Enter option: {Colors.END}")
        
        if choice == '0':
            break
        elif choice == 'a':
            new_key = get_input(f"{Colors.YELLOW}Enter new API key: {Colors.END}")
            if new_key and new_key != 'exit':
                if add_api_key(config, new_key):
                    print_colored("API key added and usage fetched successfully!", Colors.GREEN)
                else:
                    print_colored("API key already exists!", Colors.YELLOW)
        elif choice == 'r':
            if config.get("api_keys"):
                try:
                    idx = int(get_input(f"{Colors.YELLOW}Enter API key index to remove: {Colors.END}"))
                    if idx != 'exit':
                        removed = remove_api_key(config, idx)
                        if removed:
                            print_colored(f"API key {removed[:8]}... removed!", Colors.GREEN)
                        else:
                            print_colored("Invalid index!", Colors.RED)
                except ValueError:
                    print_colored("Please enter a valid number!", Colors.RED)
            else:
                print_colored("No API keys to remove!", Colors.YELLOW)
        elif choice == 's':
            if len(config.get("api_keys", [])) > 1:
                try:
                    idx = int(get_input(f"{Colors.YELLOW}Enter API key index to switch to: {Colors.END}"))
                    if idx != 'exit':
                        if switch_api_key(config, idx):
                            # Refresh usage for the new active key
                            check_and_update_usage(config, force=True)
                            print_colored(f"Switched to API key {idx}!", Colors.GREEN)
                        else:
                            print_colored("Invalid index!", Colors.RED)
                except ValueError:
                    print_colored("Please enter a valid number!", Colors.RED)
            else:
                print_colored("Only one API key available. Add more keys to switch.", Colors.YELLOW)
        elif choice == 'c':
            # Refresh all keys
            print_colored("Refreshing usage for all API keys...", Colors.CYAN)
            results = refresh_all_keys_usage(config)
            
            if results:
                success_count = 0
                for key, usage in results.items():
                    if usage and "error" not in usage:
                        success_count += 1
                print_colored(f"Refreshed {success_count}/{len(results)} keys successfully!", Colors.GREEN)
            else:
                print_colored("Could not refresh usage information!", Colors.RED)

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
        
        if not config.get("api_keys"):
            print_colored("\nNo API keys found!", Colors.RED)
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
    
    if not config.get("api_keys"):
        print_colored("\nNo API keys found!", Colors.YELLOW)
        print_colored("You need at least one API key to use this tool.", Colors.CYAN)
        
        while True:
            api_key = get_input(f"{Colors.YELLOW}Enter your GamesKinbo API key (press Enter to exit): {Colors.END}")
            if api_key == 'exit':
                print_colored("\nExiting...", Colors.CYAN)
                return
            if api_key:
                config["api_keys"] = [api_key]
                config["total_requests"] = 0
                config["current_api_index"] = 0
                save_config(config)
                
                # Fetch initial usage to set total_requests correctly
                usage = check_and_update_usage(config, force=True)
                if usage and "error" not in usage:
                    print_colored(f"API key saved! Used: {usage.get('used', 0)}/{usage.get('limit', 0)}", Colors.GREEN)
                else:
                    print_colored("API key saved! (Usage info not available yet)", Colors.GREEN)
                break
            else:
                print_colored("API key cannot be empty!", Colors.RED)
                continue
    
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
        print_colored(f"   [{Colors.YELLOW}4{Colors.END}] Manage API Keys", Colors.YELLOW)
        print_colored(f"   [{Colors.GOLD}5{Colors.END}] Display Sections", Colors.GOLD)
        print_colored(f"   [{Colors.RED}6{Colors.END}] Exit", Colors.RED)
        print_colored("─"*40, Colors.CYAN)
        
        print_colored("\n💡 TIP: Enter letter for recent player, '0' for new UID, or [1-6] for main options", Colors.CYAN)
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
                manage_api_keys(config)
                
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