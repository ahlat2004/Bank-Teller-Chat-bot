import sqlite3

conn = sqlite3.connect('data/bank_demo.db')
c = conn.cursor()

# Get schema for users table
c.execute("PRAGMA table_info(users)")
schema = c.fetchall()
print("Users table schema:")
for row in schema:
    print(f"  {row}")

# Get all users
c.execute('SELECT * FROM users ORDER BY id DESC LIMIT 5')
users = c.fetchall()
print("\nRecent users:")
for user in users:
    print(f"  {user}")
    uid = user[0]
    c.execute('SELECT id, account_type, balance FROM accounts WHERE user_id = ? ORDER BY id DESC', (uid,))
    accounts = c.fetchall()
    for acc_id, acc_type, balance in accounts:
        print(f"    - Account {acc_id}: {acc_type} (balance: {balance})")

conn.close()
