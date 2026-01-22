"""
Error Handler
Generates clear, actionable error messages for users
Place in: backend/app/utils/error_handler.py
"""

from typing import Optional, Dict, Any


class ErrorHandler:
    """
    Generates user-friendly error messages with suggestions
    """
    
    def __init__(self):
        """Initialize error handler"""
        self.currency = "PKR"
    
    def insufficient_balance_error(self, required: float, available: float,
                                   available_accounts: Optional[list] = None) -> str:
        """
        Generate insufficient balance error
        
        Args:
            required: Amount needed
            available: Amount available
            available_accounts: List of other accounts (optional)
            
        Returns:
            Formatted error message
        """
        shortfall = required - available
        
        error = f"""❌ Transfer Failed: Insufficient Balance

You need: {self.currency} {required:,.2f}
Available: {self.currency} {available:,.2f}
Shortfall: {self.currency} {shortfall:,.2f}

Suggestions:
"""
        
        if available > 0:
            error += f"• Transfer a smaller amount (up to {self.currency} {available:,.2f})\n"
        
        if available_accounts and len(available_accounts) > 0:
            error += "• Use a different account:\n"
            for acc in available_accounts[:2]:  # Show max 2 accounts
                error += f"  - {acc['account_type'].title()}: {self.currency} {acc['balance']:,.2f}\n"
        else:
            error += "• Deposit funds first\n"
        
        error += "\nView all accounts: Type 'balance'"
        
        return error.strip()
    
    def invalid_account_error(self, entered_account: str,
                              user_accounts: Optional[list] = None) -> str:
        """
        Generate invalid account number error
        
        Args:
            entered_account: Account number entered
            user_accounts: User's valid accounts (optional)
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Invalid Account Number

You entered: {entered_account}
"""
        
        # Detect format issue
        if len(entered_account) < 24:
            error += f"\nExpected format: PKXXBANKXXXXXXXXXXXXXXXX"
            error += f"\n                (24 characters for IBAN)"
            error += f"\n\nExample: PK98BANK7654321098765432"
        else:
            error += f"\nThis account number format is not recognized."
        
        if user_accounts and len(user_accounts) > 0:
            error += "\n\nYour accounts:"
            for acc in user_accounts:
                masked = acc['account_no'][:4] + "****" + acc['account_no'][-4:]
                error += f"\n• {masked} ({acc['account_type'].title()})"
        
        error += "\n\nTry again or type 'help' for assistance"
        
        return error.strip()
    
    def account_not_found_error(self, account_number: str,
                                similar_accounts: Optional[list] = None) -> str:
        """
        Generate account not found error
        
        Args:
            account_number: Account number searched
            similar_accounts: Similar account numbers (optional)
            
        Returns:
            Formatted error message
        """
        masked = account_number[:4] + "****" + account_number[-6:]
        
        error = f"""❌ Account Not Found: {masked}

This account doesn't exist in our system.
"""
        
        if similar_accounts and len(similar_accounts) > 0:
            error += "\nDid you mean one of these?"
            for acc in similar_accounts:
                masked_sim = acc[:4] + "****" + acc[-4:]
                error += f"\n• {masked_sim}"
        
        error += "\n\nPlease double-check the account number"
        
        return error.strip()
    
    def amount_out_of_range_error(self, amount: float, min_amount: float,
                                  max_amount: float) -> str:
        """
        Generate amount out of range error
        
        Args:
            amount: Amount entered
            min_amount: Minimum allowed
            max_amount: Maximum allowed
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Invalid Amount: {self.currency} {amount:,.2f}

Transfer limits:
• Minimum: {self.currency} {min_amount:,.0f}
• Maximum: {self.currency} {max_amount:,.0f} per transaction
"""
        
        if amount > max_amount:
            error += f"""
Need to transfer more?
• Split into multiple transactions
• Visit branch for high-value transfers
• Call support: 111-222-333
"""
        else:
            error += f"""
Please enter an amount between {self.currency} {min_amount:,.0f} and {self.currency} {max_amount:,.0f}
"""
        
        return error.strip()
    
    def invalid_phone_error(self, phone: str) -> str:
        """
        Generate invalid phone number error
        
        Args:
            phone: Phone number entered
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Invalid Phone Number: {phone}

Pakistani mobile format:
03XXXXXXXXX (11 digits)

Examples:
• 03001234567 ✅
• 03211234567 ✅
• 03451234567 ✅

Please enter a valid number
"""
        return error.strip()
    
    def invalid_email_error(self, email: str) -> str:
        """
        Generate invalid email error
        
        Args:
            email: Email entered
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Invalid Email Address

You entered: {email}

Please provide a valid email address.

Examples:
• user@gmail.com ✅
• name@company.com ✅
• email@domain.pk ✅
"""
        return error.strip()
    
    def email_already_exists_error(self, email: str) -> str:
        """
        Generate email already registered error
        
        Args:
            email: Email address
            
        Returns:
            Formatted error message
        """
        error = f"""⚠️  Email Already Registered

The email {email} is already associated with an account.

Already have an account?
• Type 'login' to access your account
• Type 'forgot password' for recovery
• Contact support for assistance: 111-222-333
"""
        return error.strip()
    
    def transaction_failed_error(self, reason: str = "Unknown error") -> str:
        """
        Generate general transaction failed error
        
        Args:
            reason: Failure reason
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Transaction Failed

Reason: {reason}

What you can do:
• Try again in a few moments
• Check your internet connection
• Contact support if problem persists: 111-222-333

Type 'help' for assistance
"""
        return error.strip()
    
    def bill_not_found_error(self, bill_type: str) -> str:
        """
        Generate bill not found error
        
        Args:
            bill_type: Type of bill
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Bill Not Found

No pending {bill_type} bill found.

Possible reasons:
• Bill already paid
• No bill generated yet
• Wrong bill type

View all pending bills: Type 'bills'
"""
        return error.strip()
    
    def account_frozen_error(self, account_number: str) -> str:
        """
        Generate account frozen error
        
        Args:
            account_number: Frozen account number
            
        Returns:
            Formatted error message
        """
        masked = account_number[:4] + "****" + account_number[-4:]
        
        error = f"""🔒 Account Frozen: {masked}

Your account has been temporarily frozen.

This may be due to:
• Security concerns
• Pending verification
• Administrative hold

Contact support immediately:
📞 Call: 111-222-333
📧 Email: support@bank.com
"""
        return error.strip()
    
    def otp_error(self, attempts_remaining: int) -> str:
        """
        Generate OTP verification error
        
        Args:
            attempts_remaining: Remaining verification attempts
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Invalid Verification Code

Attempts remaining: {attempts_remaining}/3

💡 Tip: Check your email for the 6-digit code
Need a new code? Reply with 'resend'
"""
        return error.strip()
    
    def otp_expired_error(self) -> str:
        """Generate OTP expired error"""
        error = """⏰ Verification Code Expired

Codes are valid for 5 minutes only.

Reply with 'resend' to get a new code
"""
        return error.strip()
    
    def max_attempts_error(self) -> str:
        """Generate max attempts exceeded error"""
        error = """🔒 Maximum Attempts Exceeded

For security, this verification session is locked.

Please try again in 15 minutes or contact support.
"""
        return error.strip()
    
    def validation_error(self, field: str, issue: str, suggestion: str = "") -> str:
        """
        Generate generic validation error
        
        Args:
            field: Field name
            issue: What's wrong
            suggestion: How to fix (optional)
            
        Returns:
            Formatted error message
        """
        error = f"""❌ Validation Error: {field}

{issue}
"""
        
        if suggestion:
            error += f"\n{suggestion}"
        
        return error.strip()
    
    def format_error_with_context(self, error_message: str,
                                  context: Optional[Dict[str, Any]] = None) -> str:
        """
        Add context information to an error
        
        Args:
            error_message: Base error message
            context: Additional context (optional)
            
        Returns:
            Enhanced error message
        """
        if not context:
            return error_message
        
        enhanced = error_message + "\n\n📋 Context:"
        
        for key, value in context.items():
            enhanced += f"\n• {key}: {value}"
        
        return enhanced


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print(" " * 20 + "ERROR HANDLER TEST")
    print("=" * 80)
    
    handler = ErrorHandler()
    
    # Test 1: Insufficient Balance
    print("\n❌ Test 1: Insufficient Balance Error")
    print("-" * 80)
    error = handler.insufficient_balance_error(
        required=5000.00,
        available=3200.00,
        available_accounts=[
            {'account_type': 'savings', 'balance': 75300.50},
            {'account_type': 'current', 'balance': 12000.00}
        ]
    )
    print(error)
    
    # Test 2: Invalid Account
    print("\n\n❌ Test 2: Invalid Account Error")
    print("-" * 80)
    error = handler.invalid_account_error(
        entered_account="PK12ABC",
        user_accounts=[
            {'account_no': 'PK12ABCD1234567890123456', 'account_type': 'salary'},
            {'account_no': 'PK12ABCD1234567890123457', 'account_type': 'savings'}
        ]
    )
    print(error)
    
    # Test 3: Amount Out of Range
    print("\n\n❌ Test 3: Amount Out of Range Error")
    print("-" * 80)
    error = handler.amount_out_of_range_error(
        amount=2500000.00,
        min_amount=1.00,
        max_amount=1000000.00
    )
    print(error)
    
    # Test 4: Invalid Phone
    print("\n\n❌ Test 4: Invalid Phone Error")
    print("-" * 80)
    error = handler.invalid_phone_error("0300123")
    print(error)
    
    # Test 5: OTP Error
    print("\n\n❌ Test 5: OTP Verification Error")
    print("-" * 80)
    error = handler.otp_error(attempts_remaining=2)
    print(error)
    
    # Test 6: Account Frozen
    print("\n\n❌ Test 6: Account Frozen Error")
    print("-" * 80)
    error = handler.account_frozen_error("PK12ABCD1234567890123456")
    print(error)
    
    print("\n" + "=" * 80)
    print("✅ Error handler tests complete!")