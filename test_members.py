#!/usr/bin/env python3
"""
Test script for Member Management System
"""

import sys
import os

# Add the BicycleRentalManagementSystem directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
bicycle_dir = os.path.join(current_dir, 'BicycleRentalManagementSystem')
sys.path.insert(0, bicycle_dir)

try:
    from database import DatabaseManager
    print("✅ Successfully imported DatabaseManager")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_member_management():
    """Test the member management functionality"""
    print("\n🚀 Testing Member Management System")
    print("=" * 50)
    
    # Initialize database
    db_manager = DatabaseManager()
    
    try:
        # Test member info retrieval
        print("\n📋 Testing member info retrieval...")
        member_info = db_manager.get_member_info(1)
        if member_info:
            print(f"✅ Member 1: {member_info['NAME']} ({member_info['EMAIL']})")
            print(f"   Type: {member_info['MEMBER_TYPE']}, Status: {member_info['STATUS']}")
            print(f"   Rental Limit: {member_info['RENTAL_LIMIT']}")
        else:
            print("❌ Failed to retrieve member info")
        
        # Test rental count
        print("\n🚲 Testing rental count...")
        rental_count = db_manager.get_member_rental_count(1)
        print(f"✅ Member 1 has {rental_count} active rentals")
        
        # Test member stats
        print("\n📊 Testing member statistics...")
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Total members
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        print(f"✅ Total members: {total_members}")
        
        # Active members
        cursor.execute("SELECT COUNT(*) FROM members WHERE STATUS = 'Active'")
        active_members = cursor.fetchone()[0]
        print(f"✅ Active members: {active_members}")
        
        # Members by type
        cursor.execute("""
            SELECT MEMBER_TYPE, COUNT(*) as count
            FROM members
            WHERE STATUS = 'Active'
            GROUP BY MEMBER_TYPE
        """)
        members_by_type = cursor.fetchall()
        print("✅ Members by type:")
        for member_type, count in members_by_type:
            print(f"   {member_type}: {count}")
        
        # Recent registrations
        cursor.execute("""
            SELECT COUNT(*) FROM members 
            WHERE REGISTRATION_DATE >= date('now', '-30 days')
        """)
        recent_registrations = cursor.fetchone()[0]
        print(f"✅ Recent registrations (30 days): {recent_registrations}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    test_member_management() 