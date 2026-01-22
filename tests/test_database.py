"""
Unit Tests for Database Operations
Tests all CRUD operations and database functionality
"""

import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager


class DatabaseTester:
    """Test suite for database operations"""
    
    def __init__(self):
        # Use a test database
        self.db = DatabaseManager('data/bank_demo_test.db')
        self.total_tests = 0
        self.passed_tests = 0
        
        # Initialize and seed
        self.db.seed_database()
    
    def assert_true(self, condition: bool, test_name: str):
        """Assert that condition is True"""
        self.total_tests += 1
        
        if condition:
            self.passed_tests += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            print(f"  ❌ {test_name}")
            return False
    
    def assert_not_none(self, value, test_name: str):
        """Assert that value is not None"""
        return self.assert_true(value is not None, test_name)
    
    def test_user_operations(self):
        """Test user CRUD operations"""
        print("\n👤 Test: User Operations")
        print("-" * 70)
        
        # Test get user by ID
        user = self.db.get_user_by_id(1)
        self.assert_not_none(user, "Get user by ID")
        self.assert_true(user['name'] == 'Ali Khan', "User name matches")
        
        # Test get user by phone
        user_by_phone = self.db.get_user_by_phone('03001234567')
        self.assert_not_none(user_by_phone, "Get user by phone")
        self.assert_true(user_by_phone['id'] == 1, "User ID matches")
    
    def test_account_operations(self):
        """Test account operations"""
        print("\n🏦 Test: Account Operations")
        print("-" * 70)
        
        # Test get user accounts
        accounts = self.db.get_user_accounts(1)
        self.assert_true(len(accounts) >= 2, "User has multiple accounts")
        
        # Test get account by number
        account = self.db.get_account_by_number('PK12ABCD1234567890123456')
        self.assert_not_none(account, "Get account by number")
        
        # Test get balance
        balance = self.db.get_balance('PK12ABCD1234567890123456')
        self.assert_true(balance > 0, "Account has positive balance")
        
        # Test update balance
        original_balance = balance
        new_balance = original_balance + 1000
        success = self.db.update_balance('PK12ABCD1234567890123456', new_balance)
        self.assert_true(success, "Update balance successful")
        
        # Verify balance updated
        updated_balance = self.db.get_balance('PK12ABCD1234567890123456')
        self.assert_true(updated_balance == new_balance, "Balance correctly updated")
    
    def test_transaction_operations(self):
        """Test transaction operations"""
        print("\n💳 Test: Transaction Operations")
        print("-" * 70)
        
        # Get account for testing
        account = self.db.get_account_by_number('PK12ABCD1234567890123456')
        
        # Test record transaction
        txn_id = self.db.record_transaction(
            account_id=account['id'],
            txn_type='credit',
            amount=5000.00,
            description='Test transaction',
            balance_after=account['balance'] + 5000
        )
        self.assert_true(txn_id > 0, "Transaction recorded with ID")
        
        # Test get transaction history
        history = self.db.get_transaction_history(account['id'], limit=5)
        self.assert_true(len(history) > 0, "Transaction history retrieved")
        
        # Test get recent transactions by account number
        recent = self.db.get_recent_transactions_by_account_no(
            'PK12ABCD1234567890123456', limit=5
        )
        self.assert_true(len(recent) > 0, "Recent transactions retrieved")
    
    def test_transfer_operations(self):
        """Test money transfer operations"""
        print("\n💸 Test: Money Transfer Operations")
        print("-" * 70)
        
        # Get initial balances
        from_balance = self.db.get_balance('PK12ABCD1234567890123456')
        to_balance = self.db.get_balance('PK98BANK7654321098765432')
        
        # Execute transfer
        success, message = self.db.execute_transfer(
            from_account_no='PK12ABCD1234567890123456',
            to_account_no='PK98BANK7654321098765432',
            amount=1000.00,
            description='Test transfer'
        )
        
        self.assert_true(success, f"Transfer executed: {message}")
        
        # Verify balances updated
        new_from_balance = self.db.get_balance('PK12ABCD1234567890123456')
        new_to_balance = self.db.get_balance('PK98BANK7654321098765432')
        
        self.assert_true(
            new_from_balance == from_balance - 1000,
            "Source account debited correctly"
        )
        self.assert_true(
            new_to_balance == to_balance + 1000,
            "Destination account credited correctly"
        )
        
        # Test insufficient balance
        success, message = self.db.execute_transfer(
            from_account_no='PK12ABCD1234567890123456',
            to_account_no='PK98BANK7654321098765432',
            amount=99999999.00,  # Huge amount
            description='Test insufficient funds'
        )
        
        self.assert_true(not success, "Transfer rejected for insufficient funds")
    
    def test_bill_operations(self):
        """Test bill operations"""
        print("\n🧾 Test: Bill Operations")
        print("-" * 70)
        
        # Test get user bills
        bills = self.db.get_user_bills(1, status='unpaid')
        self.assert_true(len(bills) > 0, "User has unpaid bills")
        
        # Test get bill by type
        elec_bill = self.db.get_bill_by_type(1, 'electricity')
        self.assert_not_none(elec_bill, "Electricity bill found")
        
        # Get account balance before payment
        account = self.db.get_account_by_number('PK12ABCD1234567890123456')
        balance_before = account['balance']
        
        # Test pay bill
        success, message = self.db.pay_bill(
            user_id=1,
            bill_type='mobile',
            amount=1800.00,
            account_no='PK12ABCD1234567890123456'
        )
        
        self.assert_true(success, f"Bill paid: {message}")
        
        # Verify balance deducted
        balance_after = self.db.get_balance('PK12ABCD1234567890123456')
        self.assert_true(
            balance_after == balance_before - 1800,
            "Bill amount deducted from account"
        )
        
        # Test insufficient balance for bill payment
        success, message = self.db.pay_bill(
            user_id=1,
            bill_type='electricity',
            amount=99999999.00,
            account_no='PK12ABCD1234567890123456'
        )
        
        self.assert_true(not success, "Bill payment rejected for insufficient funds")
    
    def test_card_operations(self):
        """Test card operations"""
        print("\n💳 Test: Card Operations")
        print("-" * 70)
        
        # Test get user cards
        cards = self.db.get_user_cards(1)
        self.assert_true(len(cards) > 0, "User has cards")
        
        # Get a card
        card = cards[0]
        
        # Test block card
        success, message = self.db.block_card(card['card_number'])
        self.assert_true(success, f"Card blocked: {message}")
        
        # Verify card is blocked
        updated_cards = self.db.get_user_cards(1)
        blocked_card = next(
            (c for c in updated_cards if c['card_number'] == card['card_number']),
            None
        )
        self.assert_true(
            blocked_card['status'] == 'blocked',
            "Card status updated to blocked"
        )
    
    def test_data_integrity(self):
        """Test data integrity and constraints"""
        print("\n🔒 Test: Data Integrity")
        print("-" * 70)
        
        # Test that all users have at least one account
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT u.id, u.name, COUNT(a.id) as account_count
                FROM users u
                LEFT JOIN accounts a ON u.id = a.user_id
                GROUP BY u.id
            """)
            results = cursor.fetchall()
            
            all_have_accounts = all(row[2] > 0 for row in results)
            self.assert_true(all_have_accounts, "All users have at least one account")
        
        # Test that all transactions reference valid accounts
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM transactions t
                LEFT JOIN accounts a ON t.account_id = a.id
                WHERE a.id IS NULL
            """)
            orphaned_txns = cursor.fetchone()[0]
            self.assert_true(
                orphaned_txns == 0,
                "No orphaned transactions (all reference valid accounts)"
            )
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 70)
        print(" " * 15 + "DATABASE OPERATIONS TEST SUITE")
        print("=" * 70)
        
        # Run all tests
        self.test_user_operations()
        self.test_account_operations()
        self.test_transaction_operations()
        self.test_transfer_operations()
        self.test_bill_operations()
        self.test_card_operations()
        self.test_data_integrity()
        
        # Print summary
        print("\n" + "=" * 70)
        print(" " * 25 + "TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n  Total Tests:     {self.total_tests}")
        print(f"  Passed:          {self.passed_tests}")
        print(f"  Failed:          {self.total_tests - self.passed_tests}")
        print(f"  Success Rate:    {success_rate:.1f}%")
        
        success = success_rate >= 90.0
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n  Target:          90% success rate")
        print(f"  Status:          {status}")
        
        print("\n" + "=" * 70)
        
        return success


def main():
    """Run database tests"""
    tester = DatabaseTester()
    success = tester.run_all_tests()
    
    # Clean up test database
    import os
    if os.path.exists('data/bank_demo_test.db'):
        os.remove('data/bank_demo_test.db')
        print("🧹 Cleaned up test database")
    
    if success:
        print("✅ All database tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Review and fix issues.")
        return 1


if __name__ == "__main__":
    exit(main())