#!/usr/bin/env python3
"""
Test script for database persistence setup
"""

import os
import sqlite3
import shutil
from datetime import datetime

def test_database_setup():
    """Test the database persistence setup"""
    
    print("🧪 Testing Database Persistence Setup")
    print("=" * 40)
    
    # Simulate Railway environment
    print("\n1. Testing Railway environment simulation...")
    
    # Test volume path logic
    VOLUME_PATH = "/app/data"
    if not os.path.exists(VOLUME_PATH):
        VOLUME_PATH = "."
        print(f"   📁 Using local path: {VOLUME_PATH}")
    else:
        print(f"   📁 Using volume path: {VOLUME_PATH}")
    
    DB_PATH = os.path.join(VOLUME_PATH, "player_stats.db")
    print(f"   🗄️  Database path: {DB_PATH}")
    
    # Test database exists
    if os.path.exists(DB_PATH):
        print(f"   ✅ Database exists")
    else:
        print(f"   ❌ Database not found")
        return False
    
    # Test database connection
    print("\n2. Testing database connection...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   📊 Found {len(tables)} tables: {[t[0] for t in tables]}")
        
        # Test a sample query
        cursor.execute("SELECT COUNT(*) FROM player_stats")
        count = cursor.fetchone()[0]
        print(f"   📈 Player stats records: {count}")
        
        conn.close()
        print("   ✅ Database connection successful")
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    # Test volume initialization simulation
    print("\n3. Testing volume initialization...")
    test_volume = "./test_volume"
    os.makedirs(test_volume, exist_ok=True)
    
    test_db_path = os.path.join(test_volume, "test_player_stats.db")
    
    if not os.path.exists(test_db_path):
        initial_db_path = "./player_stats.db"
        if os.path.exists(initial_db_path):
            shutil.copy2(initial_db_path, test_db_path)
            print(f"   ✅ Successfully copied database to test volume")
        else:
            print(f"   ❌ Initial database not found")
            return False
    
    # Test copied database
    try:
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM player_stats")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"   📈 Test volume database records: {count}")
        print("   ✅ Volume initialization test successful")
    except Exception as e:
        print(f"   ❌ Volume database test failed: {e}")
        return False
    finally:
        # Clean up test volume
        if os.path.exists(test_volume):
            shutil.rmtree(test_volume)
            print("   🧹 Cleaned up test volume")
    
    print("\n🎉 All tests passed! Database persistence setup is ready.")
    print("\n📋 Summary:")
    print("   ✅ Database path logic works")
    print("   ✅ Database connection successful") 
    print("   ✅ Volume initialization works")
    print("   ✅ Ready for Railway deployment")
    
    return True

if __name__ == "__main__":
    test_database_setup()