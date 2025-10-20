#!/usr/bin/env python3
"""
CS2 Demo Parser
Parses CS2 demo files and uploads player statistics to the API.
Only processes demos with all required players present.
"""

import os
import sys
import sqlite3
import argparse
import requests
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path

from demoparser2 import DemoParser


# Target players that must be present in the demo
REQUIRED_PLAYERS = {"nifty", "Dybbis", "Togmannen", "Stutmunn", "martinsen"}

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "player_stats.db")


def get_download_folder():
    """Get download folder from environment variable or use default .tmp/"""
    download_folder = os.getenv("download_folder")
    if not download_folder:
        download_folder = ".tmp"
        print(f"download_folder not set, using default: {download_folder}")
    return download_folder


def schedule_cleanup(demo_path: str, delay_hours: int = 3):
    """Schedule demo file cleanup after specified hours"""
    def cleanup():
        time.sleep(delay_hours * 3600)  # Convert hours to seconds
        try:
            if os.path.exists(demo_path):
                os.remove(demo_path)
                print(f"Cleaned up demo file: {demo_path}")
        except Exception as e:
            print(f"Error cleaning up {demo_path}: {e}")

    # Run cleanup in background thread
    cleanup_thread = threading.Thread(target=cleanup, daemon=True)
    cleanup_thread.start()


class DemoStatsParser:
    """Parse CS2 demo files and extract player statistics"""

    def __init__(self, demo_path: str):
        self.demo_path = demo_path
        self.parser = DemoParser(demo_path)

    def get_player_names(self) -> Set[str]:
        """Extract all player names from the demo"""
        try:
            import pandas as pd

            # Parse player info
            df = self.parser.parse_event("player_death")

            # Ensure it's a DataFrame
            if not isinstance(df, pd.DataFrame):
                print(f"Warning: player_death event returned {type(df)}, expected DataFrame")
                return set()

            # Get unique player names (both attackers and victims)
            attackers = set(df['attacker_name'].unique()) if 'attacker_name' in df.columns else set()
            victims = set(df['user_name'].unique()) if 'user_name' in df.columns else set()

            # Combine and filter out None values
            all_players = (attackers | victims) - {None, '', 'None'}

            return all_players
        except Exception as e:
            print(f"Error extracting player names: {e}")
            return set()

    def check_required_players(self) -> bool:
        """Check if all required players are present in the demo"""
        players = self.get_player_names()

        # Find which required players are present (case-insensitive)
        players_lower = {p.lower() for p in players}
        required_lower = {p.lower() for p in REQUIRED_PLAYERS}

        missing = required_lower - players_lower

        if missing:
            print(f"Missing required players: {', '.join(missing)}")
            print(f"Found players: {', '.join(sorted(players))}")
            return False

        return True

    def get_match_id(self) -> str:
        """Generate match ID from demo filename (without underscores)"""
        # Use demo filename as match ID, removing underscores for consistency
        filename = Path(self.demo_path).stem  # Get filename without extension
        match_id = filename.replace('_', '')  # Remove underscores
        return match_id

    def parse_player_stats(self) -> Dict[str, Dict]:
        """Parse player statistics from the demo"""
        try:
            import pandas as pd

            # Parse kills/deaths
            kills_df = self.parser.parse_event("player_death")

            # Ensure it's a DataFrame
            if not isinstance(kills_df, pd.DataFrame):
                print(f"Warning: kills_df is not a DataFrame, it's {type(kills_df)}")
                kills_df = pd.DataFrame()

            # Parse round end for MVPs
            # NOTE: CS2 demos do not include MVP data in the round_mvp event
            # This event is empty in CS2, unlike CSGO where it was populated
            # MVPs will always be 0 for CS2 demos
            round_mvp_df = None

            # Parse damage events
            try:
                damage_df = self.parser.parse_event("player_hurt")
                if not isinstance(damage_df, pd.DataFrame):
                    damage_df = None
            except:
                damage_df = None

            # Initialize stats dictionary
            stats = {}

            # Get all unique player names
            player_names = self.get_player_names()

            for player in player_names:
                player_lower = player.lower()

                # Only process required players
                if player_lower not in {p.lower() for p in REQUIRED_PLAYERS}:
                    continue

                # Count kills
                kills = 0
                if not kills_df.empty and 'attacker_name' in kills_df.columns:
                    kills = len(kills_df[kills_df['attacker_name'] == player])

                # Count deaths
                deaths = 0
                if not kills_df.empty and 'user_name' in kills_df.columns:
                    deaths = len(kills_df[kills_df['user_name'] == player])

                # Count headshot kills
                headshot_kills = 0
                if not kills_df.empty and 'attacker_name' in kills_df.columns and 'headshot' in kills_df.columns:
                    headshot_kills = len(kills_df[
                        (kills_df['attacker_name'] == player) &
                        (kills_df['headshot'] == True)
                    ])

                # Calculate damage
                total_dmg = 0
                utility_dmg = 0
                if damage_df is not None and not damage_df.empty and 'attacker_name' in damage_df.columns:
                    player_damage = damage_df[damage_df['attacker_name'] == player]
                    if 'dmg_health' in player_damage.columns:
                        total_dmg = int(player_damage['dmg_health'].sum())

                    # Utility damage (grenades, molotov, etc.)
                    if 'weapon' in player_damage.columns and 'dmg_health' in player_damage.columns:
                        utility_weapons = ['hegrenade', 'molotov', 'incgrenade', 'inferno']
                        utility_dmg = int(player_damage[
                            player_damage['weapon'].isin(utility_weapons)
                        ]['dmg_health'].sum())

                # Count MVPs
                # NOTE: MVPs are not available in CS2 demos, always 0
                mvps = 0

                # Count multi-kills (ace, quad, triple)
                ace_rounds = 0
                quad_rounds = 0
                triple_rounds = 0

                # Use 'round' column from round_end event, not 'round_num'
                # We need to get round info from a different source
                # Let's try parsing round_end and matching ticks
                if not kills_df.empty and 'attacker_name' in kills_df.columns and 'tick' in kills_df.columns:
                    try:
                        # Parse round_end to get round boundaries
                        round_end_df = self.parser.parse_event("round_end")
                        if isinstance(round_end_df, pd.DataFrame) and not round_end_df.empty and 'tick' in round_end_df.columns and 'round' in round_end_df.columns:
                            # Add round number to kills based on tick
                            player_kills = kills_df[kills_df['attacker_name'] == player].copy()

                            if not player_kills.empty:
                                # Assign round number based on tick
                                def get_round_for_tick(tick):
                                    for idx, row in round_end_df.iterrows():
                                        if tick <= row['tick']:
                                            return row['round']
                                    return round_end_df.iloc[-1]['round']

                                player_kills['round'] = player_kills['tick'].apply(get_round_for_tick)
                                kills_per_round = player_kills.groupby('round').size()

                                ace_rounds = len(kills_per_round[kills_per_round >= 5])
                                quad_rounds = len(kills_per_round[kills_per_round == 4])
                                triple_rounds = len(kills_per_round[kills_per_round == 3])
                    except Exception as e:
                        print(f"Warning: Could not calculate multi-kills for {player}: {e}")

                stats[player] = {
                    'kills_total': kills,
                    'deaths_total': deaths,
                    'dmg': total_dmg,
                    'utility_dmg': utility_dmg,
                    'headshot_kills_total': headshot_kills,
                    'ace_rounds_total': ace_rounds,
                    'quad_rounds_total': quad_rounds,
                    'triple_rounds_total': triple_rounds,
                    'mvps': mvps,
                }

            return stats

        except Exception as e:
            print(f"Error parsing player stats: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def parse_map_stats(self) -> Optional[Dict]:
        """Parse map statistics from the demo"""
        try:
            import pandas as pd
            import re

            header = self.parser.parse_header()
            map_name = header.get('map_name', 'unknown')

            # Parse round end events to determine winner
            round_end_df = self.parser.parse_event("round_end")

            # Ensure it's a DataFrame
            if not isinstance(round_end_df, pd.DataFrame):
                round_end_df = pd.DataFrame()

            # Determine which team won the match
            won = 0
            if not round_end_df.empty and 'winner' in round_end_df.columns and 'tick' in round_end_df.columns:
                # Get the winning side from the last round
                last_round = round_end_df.iloc[-1]
                winning_side = last_round['winner']  # 'CT' or 'T'
                last_round_tick = last_round['tick']

                # Parse player ticks to determine which side our players were on
                try:
                    ticks_df = self.parser.parse_ticks(['name', 'team_name'])

                    # Get ticks around the final round
                    relevant_ticks = ticks_df[
                        (ticks_df['tick'] >= last_round_tick - 1000) &
                        (ticks_df['tick'] <= last_round_tick)
                    ]

                    # Find which team our players were on in the final round
                    our_players_lower = {p.lower() for p in REQUIRED_PLAYERS}
                    our_team = None

                    for player_name in relevant_ticks['name'].unique():
                        if player_name and player_name.lower() in our_players_lower:
                            player_ticks = relevant_ticks[relevant_ticks['name'] == player_name]
                            if len(player_ticks) > 0 and 'team_name' in player_ticks.columns:
                                # Get most common team for this player in the final round
                                team = player_ticks['team_name'].mode()[0]
                                # Map team_name to CT/T (team_name is 'CT' or 'TERRORIST')
                                our_team = 'CT' if team == 'CT' else 'T'
                                break

                    # Determine if we won
                    if our_team:
                        won = 1 if winning_side == our_team else 0
                    else:
                        print("Warning: Could not determine our team, defaulting to loss")
                        won = 0

                except Exception as e:
                    print(f"Warning: Could not determine team from ticks: {e}")
                    # Fallback: just count rounds (less accurate due to side switching)
                    ct_wins = len(round_end_df[round_end_df['winner'] == 'CT'])
                    t_wins = len(round_end_df[round_end_df['winner'] == 'T'])
                    won = 1 if ct_wins > t_wins else 0

            # Extract date/time from filename if it matches the format YYYY_MM_DD_HH_MM.dem
            filename = Path(self.demo_path).stem
            date_time = None

            # Try to parse filename format: YYYY_MM_DD_HH_MM
            match = re.match(r'(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})', filename)
            if match:
                year, month, day, hour, minute = match.groups()
                date_time = f"{year}-{month}-{day} {hour}:{minute}:00"
                print(f"Extracted timestamp from filename: {date_time}")
            else:
                # Fallback: use file modification time
                print(f"Warning: Could not parse timestamp from filename '{filename}', using file modification time")
                mod_time = os.path.getmtime(self.demo_path)
                date_time = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

            return {
                'map_name': map_name,
                'date_time': date_time,
                'won': won,
            }

        except Exception as e:
            print(f"Error parsing map stats: {e}")
            return None


def match_exists_in_db(match_id: str) -> bool:
    """Check if a match already exists in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM map_stats WHERE match_id = ?",
            (match_id,)
        )
        count = cursor.fetchone()[0]

        conn.close()

        return count > 0

    except Exception as e:
        print(f"Error checking if match exists: {e}")
        return False


def upload_to_database(match_id: str, player_stats: Dict, map_stats: Dict) -> bool:
    """Upload stats directly to the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insert map stats
        cursor.execute("""
            INSERT INTO map_stats (match_id, map_name, date_time, won)
            VALUES (?, ?, ?, ?)
        """, (
            match_id,
            map_stats['map_name'],
            map_stats['date_time'],
            map_stats['won']
        ))

        # Insert player stats
        for player_name, stats in player_stats.items():
            cursor.execute("""
                INSERT INTO player_stats (
                    match_id, kills_total, deaths_total, dmg, utility_dmg,
                    headshot_kills_total, ace_rounds_total, quad_rounds_total,
                    triple_rounds_total, mvps, name
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                stats['kills_total'],
                stats['deaths_total'],
                stats['dmg'],
                stats['utility_dmg'],
                stats['headshot_kills_total'],
                stats['ace_rounds_total'],
                stats['quad_rounds_total'],
                stats['triple_rounds_total'],
                stats['mvps'],
                player_name
            ))

        conn.commit()
        conn.close()

        print(f"Successfully uploaded stats for match {match_id}")
        return True

    except Exception as e:
        print(f"Error uploading to database: {e}")
        import traceback
        traceback.print_exc()
        return False


def upload_to_api(match_id: str, player_stats: Dict, map_stats: Dict, api_url: str, api_token: Optional[str] = None) -> bool:
    """Upload stats via API"""
    try:
        # Prepare the payload
        payload = {
            "match_id": match_id,
            "player_stats": [
                {
                    "name": player_name,
                    "kills_total": stats['kills_total'],
                    "deaths_total": stats['deaths_total'],
                    "dmg": stats['dmg'],
                    "utility_dmg": stats['utility_dmg'],
                    "headshot_kills_total": stats['headshot_kills_total'],
                    "ace_rounds_total": stats['ace_rounds_total'],
                    "quad_rounds_total": stats['quad_rounds_total'],
                    "triple_rounds_total": stats['triple_rounds_total'],
                    "mvps": stats['mvps'],
                }
                for player_name, stats in player_stats.items()
            ],
            "map_stats": {
                "map_name": map_stats['map_name'],
                "date_time": map_stats['date_time'],
                "won": map_stats['won'],
            }
        }

        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"

        # Make the API request
        response = requests.post(
            f"{api_url}/api/upload",
            json=payload,
            headers=headers,
            timeout=30
        )

        # Check response
        if response.status_code == 200:
            print(f"Successfully uploaded stats for match {match_id} via API")
            return True
        elif response.status_code == 409:
            print(f"Match {match_id} already exists in database (via API)")
            return False
        else:
            print(f"API upload failed with status {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error uploading to API: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Unexpected error uploading to API: {e}")
        import traceback
        traceback.print_exc()
        return False


def parse_demo_file(demo_path: str, use_api: bool = True, api_url: Optional[str] = None, api_token: Optional[str] = None, cleanup: bool = False) -> bool:
    """Parse a demo file and upload stats if valid"""
    print(f"\n{'='*60}")
    print(f"Processing: {demo_path}")
    print(f"{'='*60}")

    # Initialize parser
    parser = DemoStatsParser(demo_path)

    # Check if all required players are present
    if not parser.check_required_players():
        print("Skipping demo - not all required players present")
        return False

    print("All required players found!")

    # Get match ID
    match_id = parser.get_match_id()
    print(f"Match ID: {match_id}")

    # Check if match already exists (only for direct DB mode)
    if not use_api and match_exists_in_db(match_id):
        print(f"Match {match_id} already exists in database - skipping")
        return False

    # Parse stats
    print("Parsing player stats...")
    player_stats = parser.parse_player_stats()

    if not player_stats:
        print("Failed to parse player stats")
        return False

    print(f"Parsed stats for {len(player_stats)} players")

    print("Parsing map stats...")
    map_stats = parser.parse_map_stats()

    if not map_stats:
        print("Failed to parse map stats")
        return False

    print(f"Map: {map_stats['map_name']}, Date: {map_stats['date_time']}, Won: {map_stats['won']}")

    # Upload stats
    if use_api:
        if not api_url:
            print("Error: API URL is required for API mode")
            return False
        print(f"Uploading to API at {api_url}...")
        success = upload_to_api(match_id, player_stats, map_stats, api_url, api_token)
    else:
        print("Uploading to database...")
        success = upload_to_database(match_id, player_stats, map_stats)

    # Schedule cleanup if enabled and upload was successful
    if success and cleanup:
        print(f"Scheduling cleanup of {demo_path} in 3 hours...")
        schedule_cleanup(demo_path, delay_hours=3)

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Parse CS2 demo files and upload stats",
        epilog="""
Examples:
  # Upload to API (default)
  %(prog)s demos/ --api-url https://api.example.com --api-token YOUR_TOKEN

  # Upload to local database
  %(prog)s demos/ --database

  # Process single file via API
  %(prog)s match.dem --api-url https://api.example.com

  # Use environment variables for API credentials
  export CS2_API_URL=https://api.example.com
  export CS2_API_TOKEN=YOUR_TOKEN
  %(prog)s demos/
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('demo_path', help='Path to demo file or directory containing demos')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Recursively search for demo files in directory')
    parser.add_argument('--database', '--db', action='store_true',
                       help='Upload directly to database instead of API (default: use API)')
    parser.add_argument('--api-url', type=str,
                       help='API server URL (default: from CS2_API_URL env var)')
    parser.add_argument('--api-token', type=str,
                       help='API authentication token (default: from CS2_API_TOKEN env var)')
    parser.add_argument('--clean', action='store_true',
                       help='Clean up demo files 3 hours after processing (default: from clean env var or false)')

    args = parser.parse_args()

    # Determine upload mode
    use_api = not args.database

    # Get API credentials
    api_url = args.api_url or os.getenv('CS2_API_URL')
    api_token = args.api_token or os.getenv('CS2_API_TOKEN')

    # Get cleanup setting
    cleanup = args.clean or os.getenv('clean', '').lower() == 'true'
    if cleanup:
        print("Cleanup mode: Enabled (demos will be deleted 3 hours after processing)")

    # Validate API mode requirements
    if use_api:
        if not api_url:
            print("Error: API mode requires --api-url or CS2_API_URL environment variable")
            print("Use --database flag to upload directly to database instead")
            sys.exit(1)
        print(f"Upload mode: API ({api_url})")
        if api_token:
            print("API token: configured")
        else:
            print("API token: not set (requests may fail if authentication is required)")
    else:
        print(f"Upload mode: Direct database ({DB_PATH})")

    demo_path = Path(args.demo_path)

    if not demo_path.exists():
        print(f"Error: Path {demo_path} does not exist")
        sys.exit(1)

    # Collect demo files
    demo_files = []

    if demo_path.is_file():
        if demo_path.suffix == '.dem':
            demo_files.append(demo_path)
        else:
            print(f"Error: {demo_path} is not a .dem file")
            sys.exit(1)

    elif demo_path.is_dir():
        if args.recursive:
            demo_files = list(demo_path.rglob('*.dem'))
        else:
            demo_files = list(demo_path.glob('*.dem'))

    if not demo_files:
        print("No demo files found")
        sys.exit(1)

    print(f"Found {len(demo_files)} demo file(s)")

    # Process each demo
    successful = 0
    skipped = 0
    failed = 0

    for demo_file in sorted(demo_files):
        result = parse_demo_file(
            str(demo_file),
            use_api=use_api,
            api_url=api_url,
            api_token=api_token,
            cleanup=cleanup
        )

        if result:
            successful += 1
        elif result is False:
            skipped += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total demos processed: {len(demo_files)}")
    print(f"Successfully uploaded: {successful}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
