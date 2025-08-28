import sqlite3

try:
    conn = sqlite3.connect('BicycleRental.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check members table structure
    print("\nMembers table structure:")
    cursor.execute("PRAGMA table_info(members)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULLABLE'}")
    
    # Check members data
    print("\nMembers data:")
    cursor.execute("SELECT * FROM members LIMIT 5")
    members = cursor.fetchall()
    for member in members:
        print(f"  {member}")
    
    conn.close()
    print("\nDatabase check completed!")
    
except Exception as e:
    print(f"Error: {e}") 