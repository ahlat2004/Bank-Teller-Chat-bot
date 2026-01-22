"""
Authentication Manager
Orchestrates OTP email sending and verification
Place in: backend/app/auth/auth_manager.py
"""

from typing import Tuple, Optional
from auth.email_service import EmailService
from auth.otp_manager import OTPManager


class AuthManager:
    """
    High-level authentication orchestrator
    Combines email service and OTP manager
    """
    
    def __init__(self, smtp_email: Optional[str] = None, 
                 smtp_password: Optional[str] = None,
                 db_path: str = 'data/bank_demo.db'):
        """
        Initialize authentication manager
        
        Args:
            smtp_email: Gmail address for sending emails
            smtp_password: Gmail app password
            db_path: Database path
        """
        self.email_service = EmailService(smtp_email, smtp_password)
        self.otp_manager = OTPManager(db_path)
    
    def initiate_email_verification(self, email: str, 
                                   purpose: str = 'account_creation') -> Tuple[bool, str]:
        """
        Initiate email verification process
        
        Args:
            email: Email address to verify
            purpose: Purpose of verification
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Generate OTP
            otp_code = self.otp_manager.create_otp_session(email, purpose)
            
            # Send email
            email_sent = self.email_service.send_otp_email(email, otp_code, purpose)
            
            if email_sent:
                return True, f"✉️ Verification code sent to {email}. Please check your inbox."
            else:
                return False, "Failed to send verification email. Please try again."
        
        except Exception as e:
            print(f"❌ Error initiating verification: {e}")
            return False, f"Verification error: {str(e)}"
    
    def verify_email_otp(self, email: str, otp_code: str, 
                        purpose: str = 'account_creation') -> Tuple[bool, str]:
        """
        Verify OTP code
        
        Args:
            email: Email address
            otp_code: OTP to verify
            purpose: Purpose of verification
            
        Returns:
            Tuple of (success, message)
        """
        return self.otp_manager.verify_otp(email, otp_code, purpose)
    
    def resend_verification(self, email: str, 
                          purpose: str = 'account_creation') -> Tuple[bool, str]:
        """
        Resend verification code
        
        Args:
            email: Email address
            purpose: Purpose of verification
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Generate new OTP
            new_otp = self.otp_manager.resend_otp(email, purpose)
            
            if not new_otp:
                return False, "Failed to generate new code. Please try again."
            
            # Send email
            email_sent = self.email_service.send_otp_email(email, new_otp, purpose)
            
            if email_sent:
                return True, f"✉️ New verification code sent to {email}"
            else:
                return False, "Failed to send email. Please try again."
        
        except Exception as e:
            print(f"❌ Error resending verification: {e}")
            return False, f"Error: {str(e)}"
    
    def is_email_verified(self, email: str, purpose: str = 'account_creation') -> bool:
        """
        Check if email is verified
        
        Args:
            email: Email to check
            purpose: Purpose to check
            
        Returns:
            True if verified
        """
        return self.otp_manager.is_email_verified(email, purpose)
    
    def send_welcome_email(self, email: str, name: str, account_number: str) -> bool:
        """
        Send welcome email after account creation
        
        Args:
            email: User email
            name: User name
            account_number: New account number
            
        Returns:
            True if sent successfully
        """
        return self.email_service.send_welcome_email(email, name, account_number)
    
    def require_transaction_verification(self, amount: float, 
                                        recipient: Optional[str] = None,
                                        user_id: Optional[int] = None) -> bool:
        """
        Determine if transaction requires email verification
        
        Args:
            amount: Transaction amount
            recipient: Recipient name/account (optional)
            user_id: User ID (optional)
            
        Returns:
            True if verification required
        """
        # High-value transactions
        if amount >= 25000:
            return True
        
        # Add more rules as needed:
        # - First transaction of the day
        # - New recipient
        # - Suspicious pattern
        
        return False
    
    def cleanup_expired(self):
        """Cleanup expired OTP sessions"""
        return self.otp_manager.cleanup_expired_sessions()


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "AUTH MANAGER TEST")
    print("=" * 70)
    
    # Initialize (will use environment variables for email)
    auth_mgr = AuthManager()
    
    test_email = "your-test-email@gmail.com"  # Replace with your email
    
    print(f"\n📧 Testing with email: {test_email}")
    
    # Test 1: Initiate verification
    print("\n📝 Test 1: Initiate Email Verification")
    print("-" * 70)
    # Uncomment to test:
    # success, message = auth_mgr.initiate_email_verification(test_email, 'account_creation')
    # print(f"Result: {message}")
    # print(f"Status: {'✅ Success' if success else '❌ Failed'}")
    
    print("⚠️  To test email sending:")
    print("   1. Set SMTP_EMAIL and SMTP_PASSWORD environment variables")
    print("   2. Uncomment the test code above")
    print("   3. Replace test_email with your email")
    print("   4. Run: python auth_manager.py")
    
    # Test 2: Check verification requirement
    print("\n🔍 Test 2: Check Transaction Verification Requirement")
    print("-" * 70)
    
    test_amounts = [5000, 25000, 50000, 100000]
    for amount in test_amounts:
        required = auth_mgr.require_transaction_verification(amount)
        status = "✅ Required" if required else "⭕ Not required"
        print(f"   PKR {amount:>7,.0f} → {status}")
    
    print("\n" + "=" * 70)
    print("✅ Auth manager tests complete!")