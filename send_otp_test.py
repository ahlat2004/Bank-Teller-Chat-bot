#!/usr/bin/env python3
"""
send_otp_test.py

Simple test script to trigger OTP email sending via AuthManager.
Default recipient is `apexwolf993@gmail.com` (for tester use). Do NOT hardcode recipients
in backend code — keep them here in tests.

Usage:
  python send_otp_test.py                # sends to default apexwolf993@gmail.com
  python send_otp_test.py user@example.com
  SMTP credentials are read from env vars or the email service defaults.
"""
import sys
from app.auth.auth_manager import AuthManager

DEFAULT_RECIPIENT = "apexwolf993@gmail.com"

def main():
    recipient = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RECIPIENT
    print(f"Sending OTP to: {recipient}")
    am = AuthManager()  # Uses EmailService defaults/environment
    success, message = am.initiate_email_verification(recipient, 'account_creation')
    print("Result:", success, message)

if __name__ == '__main__':
    main()
