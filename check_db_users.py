"""
Quick script to check if accounts were created in the database
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data', 'bank_demo.db')

print(f"Querying database: {db_path}\n")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    # Count users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']
    print(f"Total users in database: {total_users}")
    
    # Get recent users
    print("\nRecent users (last 5):")
    cursor.execute("SELECT id, name, phone, email, created_at FROM users ORDER BY id DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID: {row['id']}, Name: {row['name']}, Phone: {row['phone']}, Email: {row['email']}, Created: {row['created_at']}")
    
    # Count accounts
    cursor.execute("SELECT COUNT(*) as count FROM accounts")
    total_accounts = cursor.fetchone()['count']
    print(f"\nTotal accounts in database: {total_accounts}")
    
    # Get recent accounts
    print("\nRecent accounts (last 5):")
    cursor.execute("SELECT id, user_id, account_no, account_type, balance, created_at FROM accounts ORDER BY id DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID: {row['id']}, User ID: {row['user_id']}, Account: {row['account_no']}, Type: {row['account_type']}, Balance: {row['balance']}, Created: {row['created_at']}")
    
    # Check for ahmed@example.com
    print("\n\nSearching for 'ahmed' or 'example.com' users:")
    cursor.execute("SELECT * FROM users WHERE name LIKE '%ahmed%' OR email LIKE '%example%'")
    results = cursor.fetchall()
    if results:
        for row in results:
            print(f"  Found: {row['name']} ({row['email']})")
    else:
        print("  No users found with 'ahmed' or 'example.com'")
    
finally:
    conn.close()

print("\n" + "="*80)
