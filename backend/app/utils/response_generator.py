"""
Response Generator
Generates natural language responses with database data
"""

from typing import Dict, Any, Optional
from database.db_manager import DatabaseManager
from utils.receipt_generator import ReceiptGenerator
from utils.error_handler import ErrorHandler


class ResponseGenerator:
    """
    Generates conversational responses with real data
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize response generator
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.receipt_generator = ReceiptGenerator()
        self.error_handler = ErrorHandler()
    
    def generate_balance_response(self, user_id: int, account_no: Optional[str] = None) -> str:
        """
        Generate balance check response
        
        Args:
            user_id: User ID
            account_no: Specific account number (optional)
            
        Returns:
            Response message
        """
        if account_no:
            balance = self.db.get_balance(account_no)
            if balance is None:
                return "I couldn't find that account. Please check the account number."
            
            account = self.db.get_account_by_number(account_no)
            return (
                f"Your {account['account_type']} account balance is "
                f"PKR {balance:,.2f}"
            )
        else:
            # Get all user accounts
            accounts = self.db.get_user_accounts(user_id)
            if not accounts:
                return "You don't have any active accounts."
            
            if len(accounts) == 1:
                acc = accounts[0]
                return (
                    f"Your {acc['account_type']} account balance is "
                    f"PKR {acc['balance']:,.2f}"
                )
            else:
                # Multiple accounts
                response = "Here are your account balances:\n"
                for acc in accounts:
                    response += (
                        f"• {acc['account_type'].title()}: "
                        f"PKR {acc['balance']:,.2f}\n"
                    )
                return response.strip()
    
    def generate_transfer_confirmation(self, amount: float, payee: str,
                                      from_account: Optional[str] = None) -> str:
        """
        Generate transfer confirmation message
        
        Args:
            amount: Transfer amount
            payee: Recipient name/account
            from_account: Source account (optional)
            
        Returns:
            Confirmation message
        """
        if from_account:
            return (
                f"Please confirm: Transfer PKR {amount:,.2f} to {payee} "
                f"from account {from_account[-4:]}? (yes/no)"
            )
        else:
            return (
                f"Please confirm: Transfer PKR {amount:,.2f} to {payee}? (yes/no)"
            )
    
    def generate_transfer_success(self, amount: float, payee: str,
                                  new_balance: Optional[float] = None,
                                  from_account: Optional[Dict] = None,
                                  to_account: Optional[Dict] = None) -> str:
        """
        Generate transfer success message with receipt (Phase 2)
        
        Args:
            amount: Transfer amount
            payee: Recipient name/account
            new_balance: New balance after transfer (optional)
            from_account: Source account details (optional)
            to_account: Destination account details (optional)
            
        Returns:
            Success message with receipt
        """
        # If account details provided, generate professional receipt (Phase 2)
        if from_account and to_account:
            receipt = self.receipt_generator.generate_transfer_receipt(
                transaction_id=self.receipt_generator.generate_transaction_id("TXN"),
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                description="Transfer via chatbot",
                new_balance=new_balance,
                format="text"
            )
            return receipt
        
        # Fallback to simple message
        message = f"✅ Successfully transferred PKR {amount:,.2f} to {payee}."
        
        if new_balance is not None:
            message += f"\nYour new balance is PKR {new_balance:,.2f}"
        
        return message
    
    def generate_bill_payment_confirmation(self, bill_type: str, amount: float) -> str:
        """
        Generate bill payment confirmation
        
        Args:
            bill_type: Type of bill
            amount: Bill amount
            
        Returns:
            Confirmation message
        """
        return (
            f"Please confirm: Pay {bill_type} bill of PKR {amount:,.2f}? (yes/no)"
        )
    
    def generate_bill_payment_success(self, bill_type: str, amount: float,
                                     new_balance: Optional[float] = None,
                                     account: Optional[Dict] = None) -> str:
        """
        Generate bill payment success message with receipt (Phase 2)
        
        Args:
            bill_type: Type of bill
            amount: Bill amount
            new_balance: New balance after payment (optional)
            account: Account details (optional)
            
        Returns:
            Success message with receipt
        """
        # If account details provided, generate professional receipt (Phase 2)
        if account:
            receipt = self.receipt_generator.generate_bill_payment_receipt(
                transaction_id=self.receipt_generator.generate_transaction_id("BILL"),
                bill_type=bill_type,
                amount=amount,
                account=account,
                reference_no=f"BILL-{self.receipt_generator.generate_transaction_id()}",
                new_balance=new_balance,
                format="text"
            )
            return receipt
        
        # Fallback to simple message
        message = f"✅ Successfully paid {bill_type} bill of PKR {amount:,.2f}."
        
        if new_balance is not None:
            message += f"\nYour new balance is PKR {new_balance:,.2f}"
        
        return message
    
    def generate_transaction_history_response(self, user_id: int, limit: int = 10) -> str:
        """
        Generate transaction history response
        
        Args:
            user_id: User ID
            limit: Number of transactions
            
        Returns:
            Transaction history message
        """
        # Get user's first account
        accounts = self.db.get_user_accounts(user_id)
        if not accounts:
            return "You don't have any active accounts."
        
        # Get transactions
        transactions = self.db.get_transaction_history(accounts[0]['id'], limit)
        
        if not transactions:
            return "You don't have any recent transactions."
        
        response = f"Here are your last {len(transactions)} transactions:\n\n"
        
        for i, txn in enumerate(transactions, 1):
            date = txn['timestamp'][:10]  # YYYY-MM-DD
            txn_type = txn['type'].replace('_', ' ').title()
            amount = txn['amount']
            desc = txn['description'] or 'Transaction'
            
            response += (
                f"{i}. {date} - {txn_type}\n"
                f"   PKR {amount:,.2f} - {desc}\n"
            )
        
        return response.strip()
    
    def generate_pending_bills_response(self, user_id: int) -> str:
        """
        Generate pending bills response
        
        Args:
            user_id: User ID
            
        Returns:
            Pending bills message
        """
        bills = self.db.get_user_bills(user_id, status='unpaid')
        
        if not bills:
            return "You don't have any pending bills. You're all caught up! ✅"
        
        response = f"You have {len(bills)} pending bill(s):\n\n"
        
        for i, bill in enumerate(bills, 1):
            bill_type = bill['type'].replace('_', ' ').title()
            amount = bill['amount']
            due_date = bill['due_date']
            
            response += (
                f"{i}. {bill_type}\n"
                f"   PKR {amount:,.2f} - Due: {due_date}\n"
            )
        
        return response.strip()
    
    def generate_error_message(self, error_type: str, details: Optional[str] = None) -> str:
        """
        Generate error message
        
        Args:
            error_type: Type of error
            details: Additional details (optional)
            
        Returns:
            Error message
        """
        messages = {
            'account_not_found': "I couldn't find that account. Please check the account number.",
            'insufficient_balance': "You don't have sufficient balance for this transaction.",
            'invalid_amount': "The amount specified is invalid. Please provide a valid amount.",
            'transfer_failed': "The transfer couldn't be completed. Please try again.",
            'bill_not_found': "I couldn't find that bill. It may have already been paid.",
            'payment_failed': "The payment couldn't be processed. Please try again.",
            'unknown': "Something went wrong. Please try again."
        }
        
        message = messages.get(error_type, messages['unknown'])
        
        if details:
            message += f"\n{details}"
        
        return message
    
    def generate_help_message(self) -> str:
        """Generate help message with available commands"""
        return (
            "I can help you with:\n\n"
            "💰 Check Balance\n"
            "   Example: 'What's my balance?'\n\n"
            "💸 Transfer Money\n"
            "   Example: 'Transfer 5000 to Ali'\n\n"
            "🧾 Pay Bills\n"
            "   Example: 'Pay my electricity bill'\n\n"
            "📜 Transaction History\n"
            "   Example: 'Show my recent transactions'\n\n"
            "📋 View Pending Bills\n"
            "   Example: 'What bills do I have?'\n\n"
            "How can I help you today?"
        )
    
    def format_currency(self, amount: float, currency: str = "PKR") -> str:
        """
        Format currency for display
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted currency string
        """
        return f"{currency} {amount:,.2f}"
    



# Example usage
if __name__ == "__main__":
    from database.db_manager import DatabaseManager
    
    print("=" * 70)
    print(" " * 20 + "RESPONSE GENERATOR TEST")
    print("=" * 70)
    
    # Initialize
    db = DatabaseManager('data/bank_demo.db')
    rg = ResponseGenerator(db)
    
    # Test balance response
    print("\n💰 Test: Balance Response")
    print("-" * 70)
    response = rg.generate_balance_response(user_id=1)
    print(response)
    
    # Test transfer confirmation
    print("\n💸 Test: Transfer Confirmation")
    print("-" * 70)
    response = rg.generate_transfer_confirmation(5000.0, "Ali Khan")
    print(response)
    
    # Test transfer success
    print("\n✅ Test: Transfer Success")
    print("-" * 70)
    response = rg.generate_transfer_success(5000.0, "Ali Khan", 120450.0)
    print(response)
    
    # Test transaction history
    print("\n📜 Test: Transaction History")
    print("-" * 70)
    response = rg.generate_transaction_history_response(user_id=1, limit=5)
    print(response)
    
    # Test pending bills
    print("\n🧾 Test: Pending Bills")
    print("-" * 70)
    response = rg.generate_pending_bills_response(user_id=1)
    print(response)
    
    # Test help message
    print("\n❓ Test: Help Message")
    print("-" * 70)
    response = rg.generate_help_message()
    print(response)
    
    print("\n" + "=" * 70)
    print("✅ Response generator tests complete!")