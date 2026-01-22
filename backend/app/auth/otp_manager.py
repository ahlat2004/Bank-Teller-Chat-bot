"""
OTP Manager
Generates, stores, and validates OTP codes
Place in: backend/app/auth/otp_manager.py
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple
import sqlite3


class OTPManager:
    """
    Manages OTP generation, storage, and validation
    """
    
    def __init__(self, db_path: str = 'data/bank_demo.db'):
        """
        Initialize OTP manager
        
        Args:
            db_path: Path to database
        """
        self.db_path = db_path
        self.otp_length = 6
        self.otp_expiry_minutes = 5
        self.max_attempts = 3
    
    def generate_otp(self) -> str:
        """
        Generate a random 6-digit OTP
        
        Returns:
            6-digit OTP string
        """
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    def create_otp_session(self, email: str, purpose: str = 'account_creation') -> str:
        """
        Create new OTP session
        
        Args:
            email: User email address
            purpose: Purpose of OTP (account_creation, transaction, login)
            
        Returns:
            Generated OTP code
        """
        otp_code = self.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert OTP session
            cursor.execute("""
                INSERT INTO otp_sessions 
                (email, otp_code, purpose, expires_at, max_attempts)
                VALUES (?, ?, ?, ?, ?)
            """, (email, otp_code, purpose, expires_at, self.max_attempts))
            
            conn.commit()
            
            print(f"✅ OTP created for {email}: {otp_code} (expires in {self.otp_expiry_minutes} min)")
            return otp_code
            
        except Exception as e:
            print(f"❌ Error creating OTP: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def verify_otp(self, email: str, otp_code: str, purpose: str = 'account_creation') -> Tuple[bool, str]:
        """
        Verify OTP code
        
        Args:
            email: User email
            otp_code: OTP to verify
            purpose: Purpose of OTP
            
        Returns:
            Tuple of (success, message)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get latest OTP session for this email and purpose
            cursor.execute("""
                SELECT * FROM otp_sessions
                WHERE email = ? AND purpose = ? AND verified = FALSE
                ORDER BY created_at DESC
                LIMIT 1
            """, (email, purpose))
            
            session = cursor.fetchone()
            
            if not session:
                return False, "No OTP session found. Please request a new code."
            
            session_id = session['id']
            stored_otp = session['otp_code']
            expires_at = datetime.fromisoformat(session['expires_at'])
            attempts = session['attempts']
            max_attempts = session['max_attempts']
            
            # Check if expired
            if datetime.now() > expires_at:
                return False, "OTP expired. Please request a new code."
            
            # Check max attempts
            if attempts >= max_attempts:
                return False, f"Maximum verification attempts ({max_attempts}) exceeded. Please request a new code."
            
            # Increment attempts
            cursor.execute("""
                UPDATE otp_sessions
                SET attempts = attempts + 1
                WHERE id = ?
            """, (session_id,))
            
            conn.commit()
            
            # Verify OTP
            if otp_code == stored_otp:
                # Mark as verified
                cursor.execute("""
                    UPDATE otp_sessions
                    SET verified = TRUE
                    WHERE id = ?
                """, (session_id,))
                
                conn.commit()
                
                print(f"✅ OTP verified for {email}")
                return True, "OTP verified successfully!"
            else:
                remaining = max_attempts - attempts - 1
                if remaining > 0:
                    return False, f"Invalid OTP. {remaining} attempt(s) remaining."
                else:
                    return False, "Invalid OTP. Maximum attempts exceeded. Please request a new code."
        
        except Exception as e:
            print(f"❌ Error verifying OTP: {e}")
            return False, f"Verification error: {str(e)}"
        
        finally:
            conn.close()
    
    def is_email_verified(self, email: str, purpose: str = 'account_creation') -> bool:
        """
        Check if email has been verified for a purpose
        
        Args:
            email: Email to check
            purpose: Purpose to check
            
        Returns:
            True if verified, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check for verified session within last 30 minutes
            cutoff = datetime.now() - timedelta(minutes=30)
            
            cursor.execute("""
                SELECT COUNT(*) FROM otp_sessions
                WHERE email = ? AND purpose = ? AND verified = TRUE
                AND created_at > ?
            """, (email, purpose, cutoff))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        finally:
            conn.close()
    
    def cleanup_expired_sessions(self):
        """Remove expired OTP sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete sessions older than 1 hour
            cutoff = datetime.now() - timedelta(hours=1)
            
            cursor.execute("""
                DELETE FROM otp_sessions
                WHERE created_at < ?
            """, (cutoff,))
            
            deleted = cursor.rowcount
            conn.commit()
            
            if deleted > 0:
                print(f"🧹 Cleaned up {deleted} expired OTP sessions")
            
            return deleted
            
        finally:
            conn.close()
    
    def resend_otp(self, email: str, purpose: str = 'account_creation') -> Optional[str]:
        """
        Resend OTP (invalidate old one and create new)
        
        Args:
            email: Email address
            purpose: Purpose of OTP
            
        Returns:
            New OTP code or None if failed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Invalidate old OTPs for this email/purpose
            cursor.execute("""
                UPDATE otp_sessions
                SET verified = FALSE, attempts = max_attempts
                WHERE email = ? AND purpose = ? AND verified = FALSE
            """, (email, purpose))
            
            conn.commit()
            
            # Create new OTP
            return self.create_otp_session(email, purpose)
            
        except Exception as e:
            print(f"❌ Error resending OTP: {e}")
            return None
        
        finally:
            conn.close()


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "OTP MANAGER TEST")
    print("=" * 70)
    
    # Initialize
    otp_mgr = OTPManager('data/bank_demo.db')
    
    # Test email
    test_email = "test@example.com"
    
    # Test 1: Generate OTP
    print("\n📝 Test 1: Generate OTP")
    print("-" * 70)
    otp = otp_mgr.create_otp_session(test_email, 'account_creation')
    print(f"Generated OTP: {otp}")
    
    # Test 2: Verify correct OTP
    print("\n✅ Test 2: Verify Correct OTP")
    print("-" * 70)
    success, message = otp_mgr.verify_otp(test_email, otp, 'account_creation')
    print(f"Result: {message}")
    print(f"Status: {'✅ Pass' if success else '❌ Fail'}")
    
    # Test 3: Verify wrong OTP
    print("\n❌ Test 3: Verify Wrong OTP")
    print("-" * 70)
    otp2 = otp_mgr.create_otp_session("test2@example.com", 'transaction')
    success, message = otp_mgr.verify_otp("test2@example.com", "999999", 'transaction')
    print(f"Result: {message}")
    print(f"Status: {'✅ Expected fail' if not success else '❌ Unexpected success'}")
    
    # Test 4: Check verification status
    print("\n🔍 Test 4: Check Verification Status")
    print("-" * 70)
    is_verified = otp_mgr.is_email_verified(test_email, 'account_creation')
    print(f"Email verified: {'✅ Yes' if is_verified else '❌ No'}")
    
    # Test 5: Cleanup
    print("\n🧹 Test 5: Cleanup Expired Sessions")
    print("-" * 70)
    deleted = otp_mgr.cleanup_expired_sessions()
    print(f"Deleted: {deleted} sessions")
    
    print("\n" + "=" * 70)
    print("✅ OTP manager tests complete!")