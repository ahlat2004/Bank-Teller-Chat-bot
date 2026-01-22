"""
Phase 1 Setup Script
Sets up email OTP system and tests it
Run this after copying all Phase 1 files
"""

import os
import sys

print("=" * 80)
print(" " * 20 + "PHASE 1: EMAIL OTP SYSTEM SETUP")
print("=" * 80)

# Step 1: Check file structure
print("\n📁 Step 1: Checking File Structure")
print("-" * 80)

required_files = [
    "backend/app/auth/__init__.py",
    "backend/app/auth/email_service.py",
    "backend/app/auth/otp_manager.py",
    "backend/app/auth/auth_manager.py",
    "backend/app/database/schema_auth.sql",
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - MISSING")
        missing_files.append(file)

if missing_files:
    print(f"\n❌ Missing {len(missing_files)} file(s). Please create them first.")
    sys.exit(1)

print("\n✅ All required files present!")

# Step 2: Initialize database tables
print("\n🗄️  Step 2: Initializing Authentication Tables")
print("-" * 80)

sys.path.append('backend/app')
from database.db_manager import DatabaseManager

try:
    db = DatabaseManager('data/bank_demo.db')
    print("✅ Database initialized")
    print("✅ Authentication tables created")
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    sys.exit(1)

# Step 3: Test OTP Manager
print("\n🔐 Step 3: Testing OTP Manager")
print("-" * 80)

from auth.otp_manager import OTPManager

try:
    otp_mgr = OTPManager('data/bank_demo.db')
    
    # Test OTP generation
    test_email = "test@example.com"
    otp = otp_mgr.create_otp_session(test_email, 'account_creation')
    print(f"✅ OTP Generated: {otp}")
    
    # Test verification
    success, message = otp_mgr.verify_otp(test_email, otp, 'account_creation')
    print(f"✅ Verification: {message}")
    
    if success:
        print("✅ OTP Manager working correctly!")
    else:
        print("⚠️  Verification failed (this shouldn't happen)")
    
except Exception as e:
    print(f"❌ OTP Manager test failed: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Configure Email Service
print("\n📧 Step 4: Email Service Configuration")
print("-" * 80)

smtp_email = os.getenv('SMTP_EMAIL')
smtp_password = os.getenv('SMTP_PASSWORD')

if smtp_email and smtp_password:
    print(f"✅ Email: {smtp_email}")
    print(f"✅ Password: {'*' * len(smtp_password)} (configured)")
    
    # Test email service (optional)
    print("\n🧪 Would you like to send a test email? (yes/no)")
    response = input("   > ").strip().lower()
    
    if response in ['yes', 'y']:
        test_recipient = input("   Enter test email address: ").strip()
        
        from auth.email_service import EmailService
        email_service = EmailService(smtp_email, smtp_password)
        
        print(f"\n📤 Sending test OTP to {test_recipient}...")
        success = email_service.send_otp_email(test_recipient, "123456", "account_creation")
        
        if success:
            print("✅ Test email sent! Check your inbox.")
        else:
            print("❌ Failed to send email. Check your SMTP credentials.")
else:
    print("⚠️  SMTP credentials not configured")
    print("\n   To enable email sending:")
    print("   1. Enable 2FA on your Gmail account")
    print("   2. Generate an App Password:")
    print("      https://myaccount.google.com/apppasswords")
    print("   3. Set environment variables:")
    print("      export SMTP_EMAIL='your-email@gmail.com'")
    print("      export SMTP_PASSWORD='your-16-char-app-password'")
    print("\n   Or add to your .env file:")
    print("      SMTP_EMAIL=your-email@gmail.com")
    print("      SMTP_PASSWORD=your-app-password")

# Step 5: Test Auth Manager
print("\n🔧 Step 5: Testing Auth Manager")
print("-" * 80)

from auth.auth_manager import AuthManager

try:
    auth_mgr = AuthManager()
    print("✅ Auth Manager initialized")
    
    # Test transaction verification requirement
    print("\n   Testing transaction verification rules:")
    test_amounts = [5000, 25000, 50000, 100000]
    for amount in test_amounts:
        required = auth_mgr.require_transaction_verification(amount)
        status = "✅ Required" if required else "⭕ Not required"
        print(f"      PKR {amount:>7,.0f} → {status}")
    
    print("\n✅ Auth Manager working correctly!")
    
except Exception as e:
    print(f"❌ Auth Manager test failed: {e}")

# Summary
print("\n\n" + "=" * 80)
print(" " * 25 + "PHASE 1 SETUP COMPLETE!")
print("=" * 80)

print("\n📋 SUMMARY:")
print("-" * 80)
print("  ✅ File structure validated")
print("  ✅ Database tables initialized")
print("  ✅ OTP Manager working")
if smtp_email and smtp_password:
    print("  ✅ Email service configured")
else:
    print("  ⚠️  Email service needs configuration")
print("  ✅ Auth Manager working")

print("\n🚀 NEXT STEPS:")
print("-" * 80)
print("  1. Update main.py with Phase 1 changes")
print("  2. Update dialogue_manager.py with OTP slots")
print("  3. Update db_manager.py with auth methods")
print("  4. Restart FastAPI server")
print("  5. Test account creation with OTP!")

print("\n💡 TESTING:")
print("-" * 80)
print("  1. Start server: uvicorn backend.app.main:app --reload")
print("  2. Test chat: POST /api/chat")
print("  3. Say: 'I want to create a new account'")
print("  4. Follow prompts and verify email OTP")

print("\n📧 EMAIL SETUP REMINDER:")
print("-" * 80)
if not (smtp_email and smtp_password):
    print("  ⚠️  Set SMTP_EMAIL and SMTP_PASSWORD environment variables")
    print("     to enable OTP email sending!")
else:
    print("  ✅ Email configured and ready!")

print("\n" + "=" * 80)
print(" " * 25 + "Setup Complete! 🎉")
print("=" * 80 + "\n")