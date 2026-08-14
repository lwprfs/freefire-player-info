from datetime import datetime
from .data import load_rank_data

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

def print_colored(text, color=Colors.END, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.END}")
    else:
        print(f"{color}{text}{Colors.END}")