#!/usr/bin/env python3
"""
Database Update Utility for CS2 Player Stats
Provides easy methods to update the SQLite database locally or on Railway
"""

import sqlite3
import os
import json
import csv
import sys
from datetime import datetime
from typing import Dict, List, Any

class DatabaseUpdater:
    def __init__(self, local=False):
        """Initialize database updater
        
        Args:
            local (bool): If True, use local database. If False, use Railway volume path.
        """
        if local or not os.path.exists("/app/data"):
            self.db_path = "./player_stats.db"
            print("🏠 Using LOCAL database")
        else:
            self.db_path = "/app/data/player_stats.db"
            print("☁️  Using RAILWAY database")
        
        print(f"📁 Database path: {self.db_path}")
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}")
    
    def backup_database(self) -> str:
        """Create a backup of the current database"""
        import shutil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.db_path}.backup_{timestamp}"
        shutil.copy2(self.db_path, backup_path)
        print(f"💾 Backup created: {backup_path}")
        return backup_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_player_stats(self, stats_data: Dict[str, Any]) -> bool:
        """Add new player statistics record
        
        Args:
            stats_data: Dictionary with player stats data
            
        Returns:
            bool: True if successful
        """
        required_fields = ['match_id', 'kills_total', 'deaths_total', 'dmg', 'name']
        for field in required_fields:
            if field not in stats_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults for optional fields
        defaults = {
            'utility_dmg': 0, 'headshot_kills_total': 0,
            'ace_rounds_total': 0, 'quad_rounds_total': 0, 
            'triple_rounds_total': 0, 'mvps': 0,
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in stats_data:
                stats_data[key] = default_value
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO player_stats 
                (match_id, kills_total, deaths_total, dmg, utility_dmg, 
                 headshot_kills_total, ace_rounds_total, 
                 quad_rounds_total, triple_rounds_total, mvps, name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stats_data['match_id'], stats_data['kills_total'], stats_data['deaths_total'],
                stats_data['dmg'], stats_data['utility_dmg'], stats_data['headshot_kills_total'],
                stats_data['ace_rounds_total'], stats_data['quad_rounds_total'],
                stats_data['triple_rounds_total'], stats_data['mvps'],
                stats_data['name'], stats_data['created_at']
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Added player stats for {stats_data['name']} in match {stats_data['match_id']}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding player stats: {e}")
            return False
    
    def update_player_stats(self, match_id: str, player_name: str, updates: Dict[str, Any]) -> bool:
        """Update existing player statistics
        
        Args:
            match_id: Match ID to update
            player_name: Player name to update
            updates: Dictionary of fields to update
            
        Returns:
            bool: True if successful
        """
        if not updates:
            print("⚠️  No updates provided")
            return False
        
        # Build SET clause
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.extend([match_id, player_name])
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                UPDATE player_stats 
                SET {set_clause}
                WHERE match_id = ? AND name = ?
            """, values)
            
            if cursor.rowcount == 0:
                print(f"⚠️  No records found for {player_name} in match {match_id}")
                return False
            
            conn.commit()
            conn.close()
            print(f"✅ Updated {cursor.rowcount} record(s) for {player_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating player stats: {e}")
            return False
    
    def delete_player_stats(self, match_id: str, player_name: str = None) -> bool:
        """Delete player statistics
        
        Args:
            match_id: Match ID to delete
            player_name: Optional player name (if None, deletes all players for match)
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if player_name:
                cursor.execute("DELETE FROM player_stats WHERE match_id = ? AND name = ?", 
                             (match_id, player_name))
                print(f"🗑️  Deleted stats for {player_name} in match {match_id}")
            else:
                cursor.execute("DELETE FROM player_stats WHERE match_id = ?", (match_id,))
                print(f"🗑️  Deleted all stats for match {match_id}")
            
            conn.commit()
            conn.close()
            print(f"✅ Deleted {cursor.rowcount} record(s)")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting player stats: {e}")
            return False
    
    def import_from_csv(self, csv_file_path: str) -> bool:
        """Import player stats from CSV file
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            bool: True if successful
        """
        try:
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                imported_count = 0
                
                for row in reader:
                    if self.add_player_stats(row):
                        imported_count += 1
                
                print(f"📊 Imported {imported_count} records from {csv_file_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error importing from CSV: {e}")
            return False
    
    def export_to_csv(self, output_file: str) -> bool:
        """Export player stats to CSV file
        
        Args:
            output_file: Output CSV file path
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM player_stats")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(player_stats)")
            columns = [row[1] for row in cursor.fetchall()]
            
            with open(output_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(columns)
                writer.writerows(rows)
            
            conn.close()
            print(f"📄 Exported {len(rows)} records to {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
    
    def get_stats_summary(self):
        """Print database statistics summary"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get table counts
            tables = ['player_stats', 'map_stats', 'chicken_kills', 'locations', 'rank']
            
            print("\n📊 Database Summary:")
            print("=" * 30)
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:15}: {count:6} records")
            
            # Get recent activity
            cursor.execute("""
                SELECT name, COUNT(*) as matches, MAX(created_at) as last_match
                FROM player_stats 
                GROUP BY name 
                ORDER BY matches DESC 
                LIMIT 5
            """)
            
            print("\n🏆 Top Players by Matches:")
            print("-" * 30)
            for row in cursor.fetchall():
                print(f"{row[0]:15}: {row[1]:3} matches (last: {row[2][:10]})")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error getting summary: {e}")

def main():
    """Command line interface for database updates"""
    if len(sys.argv) < 2:
        print("""
🔄 CS2 Database Updater

Usage:
    python update_database.py <command> [options]

Commands:
    summary                     - Show database summary
    backup                      - Create database backup
    add <json_data>            - Add player stats (JSON string)
    update <match_id> <player> <json_updates> - Update player stats
    delete <match_id> [player] - Delete player stats
    import-csv <file>          - Import from CSV file
    export-csv <file>          - Export to CSV file

Examples:
    python update_database.py summary
    python update_database.py backup
    python update_database.py add '{"match_id":"123","name":"Player1","kills_total":25,"deaths_total":10,"dmg":2500}'
    python update_database.py update 123 Player1 '{"kills_total":30}'
    python update_database.py delete 123 Player1
    python update_database.py import-csv new_stats.csv
        """)
        return
    
    command = sys.argv[1]
    
    try:
        updater = DatabaseUpdater(local=True)  # Use local=False for Railway
        
        if command == "summary":
            updater.get_stats_summary()
            
        elif command == "backup":
            updater.backup_database()
            
        elif command == "add" and len(sys.argv) >= 3:
            data = json.loads(sys.argv[2])
            updater.add_player_stats(data)
            
        elif command == "update" and len(sys.argv) >= 5:
            match_id = sys.argv[2]
            player_name = sys.argv[3]
            updates = json.loads(sys.argv[4])
            updater.update_player_stats(match_id, player_name, updates)
            
        elif command == "delete" and len(sys.argv) >= 3:
            match_id = sys.argv[2]
            player_name = sys.argv[3] if len(sys.argv) >= 4 else None
            updater.delete_player_stats(match_id, player_name)
            
        elif command == "import-csv" and len(sys.argv) >= 3:
            updater.import_from_csv(sys.argv[2])
            
        elif command == "export-csv" and len(sys.argv) >= 3:
            updater.export_to_csv(sys.argv[2])
            
        else:
            print("❌ Invalid command or missing arguments")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()