#!/usr/bin/env python3
"""
Seed demo data for testing
Creates a test user with accounts and transactions
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database.db_manager import DatabaseManager

def seed_demo_data():
    """Create demo user with test accounts"""
    db = DatabaseManager('data/bank_demo.db')
    
    print("=" * 70)
    print("SEEDING DEMO DATA")
    print("=" * 70)
    
    # Create test user
    user_success, user_msg, user_id = db.create_user(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890"
    )
    
    if user_success:
        print(f"✓ Created user: {user_id} - {user_msg}")
    else:
        print(f"✗ Failed to create user: {user_msg}")
        return
    
    # Create accounts
    accounts_data = [
        {'type': 'salary', 'balance': 50000.0},
        {'type': 'savings', 'balance': 25000.0},
        {'type': 'current', 'balance': 10000.0},
    ]
    
    account_numbers = []
    for acc_data in accounts_data:
        acc_success, acc_msg, account_no = db.create_account(
            user_id=user_id,
            account_type=acc_data['type'],
            initial_balance=acc_data['balance']
        )
        
        if acc_success:
            account_numbers.append(account_no)
            print(f"✓ Created {acc_data['type']} account: {account_no} - Balance: PKR {acc_data['balance']:,.2f}")
        else:
            print(f"✗ Failed to create account: {acc_msg}")
    
    # Add sample transactions
    if len(account_numbers) >= 2:
        # Transfer from salary to savings
        transfer_success, transfer_msg = db.execute_transfer(
            from_account_no=account_numbers[0],
            to_account_no=account_numbers[1],
            amount=5000.0,
            description="Monthly savings transfer"
        )
        
        if transfer_success:
            print(f"✓ Created sample transaction: {transfer_msg}")
        else:
            print(f"✗ Failed to create transaction: {transfer_msg}")
    
    print("=" * 70)
    print("DEMO DATA SEEDED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nTest Credentials:")
    print(f"  User ID: {user_id}")
    print(f"  Name: John Doe")
    print(f"  Email: john@example.com")
    print(f"  Phone: +1234567890")
    print(f"\nAccounts:")
    for i, acc_no in enumerate(account_numbers):
        print(f"  Account {i+1}: {acc_no}")
    print()

if __name__ == "__main__":
    seed_demo_data()
