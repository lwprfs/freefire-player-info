# Free Fire Player Info Checker

A powerful Python-based CLI tool to fetch and display detailed Free Fire player information using the GamesKinbo API. Features colorful terminal output, asset integration, player history tracking, and player comparison functionality.

## Features

- 🔍 **Fetch Player Information** - Get detailed player stats including ranks, account info, equipped items, and more
- 🎨 **Colorful Output** - Beautiful terminal output with color-coded sections and rarity indicators
- 📦 **Asset Integration** - Automatically matches item IDs with descriptions, rarity colors, and CDN links from the assets folder
- 📊 **Player History** - Automatically saves checked players to a local database
- 🔄 **Change Detection** - Shows what changed when checking the same player again
- ⚖️ **Player Comparison** - Compare stats between two players side by side
- 📁 **JSON Export** - Export player data to JSON files
- 🎮 **Recent Players** - Quick access to recently checked players using letter shortcuts
- 📈 **API Usage Tracking** - Tracks total API requests made

## Prerequisites

- Python 3.6 or higher
- `requests` library

## Installation

1. Clone or download the repository:
```bash
git clone https://github.com/lwprfs/freefire-player-info
cd freefire-player-info
```

2. Install required dependencies:

```bash
pip install requests
```

3. Run tge python code to configure it.
```bash
python free-fire.py
```
Configuration

API Key

1. Get your free API key from GamesKinbo Dashboard
2. The tool will prompt you to enter the API key on first run
3. API key is saved locally in config.json

· Free Tier: 100 requests per month

Files Created Automatically

File Purpose
config.json Stores API key and request count
players_db.json Database of all checked players
rank_data.json BR and CS rank definitions
assets/ Item data and CDN links

Usage

Run the script:

```bash
python free-fire.py
```

Menu Options

Recent Players

· Type a, b, c, etc. to instantly view a recent player's info
· Type 0 to check a new UID

Main Options

Option Description
1 Check a new player UID
2 View history of checked players
3 Compare two players
4 Change API key
5 Exit the program

Commands

· Press Enter at any prompt to cancel or exit
· Type y to confirm actions (export, delete, etc.)

Output Example

```
==================================================
 PLAYER INFO
==================================================

PlayerName
Level 69 • 9492 Likes
ID opened: March 26, 2021 at 02:21 PM

==================================================
 ACCOUNT INFO
==================================================
UID: 1234567890
Name: PlayerName
Level: 69
Region: BD
Likes: 9492
Season ID: 52
Credit Score: 100
Title: 904090025 (Paloma)
Bio: Free Fire! Battle in Style!
Gender: Gender_MALE
Language: Language_EN
Time Active: TimeActive_NIGHT
Mode Prefer: ModePrefer_BR
Rank Show: RankShow_BR

==================================================
 ACCOUNT ACTIVITY
==================================================
Release Version: OB54
Account Type: 1
BR Rank: Heroic (4712 RP)
BR Max Rank: 323
CS Rank: Heroic (78★)
CS Max Rank: 315
Created At: March 26, 2021 at 02:21 PM
Last Login: August 3, 2026 at 01:30 PM

==================================================
 EQUIPPED ITEMS
==================================================
Avatar ID: 902027015 (Paloma)
Banner ID: 901027035
BP Badges: 1
BP ID: 1001000099
Show BR Rank: Yes
Show CS Rank: Yes

==================================================
 OUTFIT
==================================================
  Item 1: 211037069
  Item 2: 203037058
  Item 3: 211000705

==================================================
 WEAPONS
==================================================
  Weapon 1: 907103421
  Weapon 2: 912037002

==================================================
 PET DETAILS
==================================================
Pet ID: 1300000101
Pet Level: 7
Pet Exp: 6000
Pet Selected: Yes
Pet Skill ID: 1315000009
Pet Skin ID: 1310000108

==================================================
 GUILD INFO
==================================================
Guild Name: Example Guild
Guild ID: 3089597273
Guild Level: 1
Guild Members: 15/30
Guild Owner: 5372836072

==================================================
 GUILD LEADER
==================================================

LeaderName
UID: 5372836072
Level: 67
Likes: 7340
BR Rank: 325 (6223 RP)
CS Rank: 301
Created At: February 16, 2022 at 05:25 PM
Last Login: July 24, 2026 at 10:52 PM

==================================================
 API USAGE
==================================================
Total API Requests: 47
```

Data Sources

· API: GamesKinbo API Documentation
  · Free tier: 100 requests/month
  · Region support: BD, IND, BR, US, ID, SG, PK
· Item Data: ItemID2 Repository
  · Contains item descriptions, rarity colors, and CDN links
  · Place in assets/ folder

File Structure

```
FF/
├── free-fire.py          # Main application
├── config.json           # API key and settings
├── players_db.json       # Player database
├── rank_data.json        # Rank definitions
├── assets/               # Item data folder
│   ├── cdn.json          # CDN links for items
│   └── itemData.json     # Item descriptions and metadata
└── README.md            # This file
```

Rank Systems

BR Rank (RP-based)

· Bronze I-III: 700-1000 RP
· Silver I-III: 1001-1300 RP
· Gold I-IV: 1301-1800 RP
· Platinum I-IV: 1801-2300 RP
· Diamond I-IV: 2301-3200 RP
· Heroic: 3201-6000 RP
· Master: 6001+ RP

CS Rank (Star-based)

· Silver III: 0 stars
· Gold I-IV: 1-16 stars
· Platinum I-IV: 17-36 stars
· Diamond I-V: 37-81 stars
· Heroic: 82-106 stars
· Elite Heroic: 107-131 stars
· Master: 132-156 stars
· Grandmaster: 157+ stars

Credits

· API: GamesKinbo - https://api.gameskinbo.com

· Item Data: ItemID2 - https://github.com/0xMe/ItemID2

License

This project is for educational purposes. Please respect the API terms of service and rate limits.

Disclaimer

This tool is not affiliated with Garena or Free Fire. All data is fetched through the GamesKinbo API. Use responsibly and respect the API usage limits (100 free requests/month).
