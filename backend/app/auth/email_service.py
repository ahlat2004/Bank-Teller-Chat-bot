"""
Email Service
Sends OTP emails using SMTP (Gmail)
Place in: backend/app/auth/email_service.py
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from datetime import datetime


class EmailService:
    """
    Handles sending OTP emails via Gmail SMTP
    """
    
    def __init__(self, smtp_email: Optional[str] = None, smtp_password: Optional[str] = None):
        """
        Initialize email service
        
        Args:
            smtp_email: Gmail address (e.g., yourbot@gmail.com)
            smtp_password: Gmail app password (not regular password!)
        """
        # Use provided credentials, environment variables, or (as a last resort) hard-coded defaults
        # WARNING: Storing credentials in source is insecure. Remove before committing to VCS.
        hardcoded_email = 'talhamughal1805@gmail.com'
        hardcoded_password = 'qasf rplo oiiu nmmv'
        self.smtp_email = smtp_email or os.getenv('SMTP_EMAIL') or hardcoded_email
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD') or hardcoded_password
        
        # Gmail SMTP settings
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587
        
        # Email settings
        self.from_name = "Bank Teller Assistant"
        self.from_email = self.smtp_email
    
    def send_otp_email(self, to_email: str, otp_code: str, 
                      purpose: str = "account_creation") -> bool:
        """
        Send OTP verification email
        
        Args:
            to_email: Recipient email address
            otp_code: 6-digit OTP code
            purpose: Purpose of OTP (account_creation, transaction, login)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = self._get_subject(purpose)
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            
            # Create HTML and plain text versions
            text_content = self._create_text_email(otp_code, purpose)
            html_content = self._create_html_email(otp_code, purpose)
            
            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ OTP email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send OTP email: {e}")
            return False
    
    def _get_subject(self, purpose: str) -> str:
        """Get email subject based on purpose"""
        subjects = {
            'account_creation': '🔐 Your Account Verification Code',
            'transaction': '🔐 Transaction Verification Code',
            'login': '🔐 Login Verification Code'
        }
        return subjects.get(purpose, '🔐 Verification Code')
    
    def _create_text_email(self, otp_code: str, purpose: str) -> str:
        """Create plain text email content"""
        purpose_text = {
            'account_creation': 'complete your account registration',
            'transaction': 'verify your transaction',
            'login': 'log in to your account'
        }
        
        action = purpose_text.get(purpose, 'verify your identity')
        
        return f"""
Bank Teller Assistant - Verification Code

Your verification code is: {otp_code}

Use this code to {action}.

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.

---
Bank Teller Assistant
Automated Banking Service
        """.strip()
    
    def _create_html_email(self, otp_code: str, purpose: str) -> str:
        """Create HTML email content"""
        purpose_text = {
            'account_creation': 'complete your account registration',
            'transaction': 'verify your transaction',
            'login': 'log in to your account'
        }
        
        action = purpose_text.get(purpose, 'verify your identity')
        current_year = datetime.now().year
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px;">🔐 Verification Code</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; opacity: 0.9;">Bank Teller Assistant</p>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                Hello,
                            </p>
                            <p style="margin: 0 0 30px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                Use this verification code to {action}:
                            </p>
                            
                            <!-- OTP Code Box -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <div style="background-color: #f8f9fa; border: 2px dashed #667eea; border-radius: 10px; padding: 20px; display: inline-block;">
                                            <span style="font-size: 36px; font-weight: bold; color: #667eea; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                                {otp_code}
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Warning -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 30px;">
                                <tr>
                                    <td style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px;">
                                        <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                                            ⏰ <strong>Important:</strong> This code will expire in 5 minutes.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 30px 0 0 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                If you didn't request this code, please ignore this email or contact support.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px;">
                                Bank Teller Assistant
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">
                                Automated Banking Service | © {current_year}
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """.strip()
    
    def send_welcome_email(self, to_email: str, name: str, account_number: str) -> bool:
        """
        Send welcome email after account creation
        
        Args:
            to_email: User email
            name: User name
            account_number: New account number
            
        Returns:
            True if sent successfully
        """
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = '🎉 Welcome to Bank Teller Assistant!'
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; overflow: hidden;">
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px;">🎉 Welcome!</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px;">
                                Dear {name},
                            </p>
                            <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px;">
                                Your account has been successfully created! 🎊
                            </p>
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 20px 0;">
                                <tr>
                                    <td style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                                        <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px;">Account Number</p>
                                        <p style="margin: 0; color: #667eea; font-size: 20px; font-weight: bold; font-family: monospace;">
                                            {account_number}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 20px 0; color: #333333; font-size: 16px;">
                                You can now:
                            </p>
                            <ul style="color: #333333; font-size: 16px; line-height: 1.8;">
                                <li>Check your balance</li>
                                <li>Transfer money</li>
                                <li>Pay bills</li>
                                <li>View transaction history</li>
                            </ul>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center;">
                            <p style="margin: 0; color: #666666; font-size: 14px;">
                                Bank Teller Assistant | Automated Banking Service
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
            """
            
            part = MIMEText(html_content, 'html')
            message.attach(part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Welcome email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {e}")
            return False


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "EMAIL SERVICE TEST")
    print("=" * 70)
    
    # Initialize (use environment variables)
    email_service = EmailService()
    
    # Test OTP email (REPLACE WITH YOUR EMAIL)
    test_email = "your-test-email@gmail.com"
    test_otp = "123456"
    
    print(f"\n📧 Sending test OTP to {test_email}...")
    print(f"   OTP Code: {test_otp}")
    
    # Uncomment to test:
    # success = email_service.send_otp_email(test_email, test_otp, "account_creation")
    # print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n⚠️  To use this service:")
    print("   1. Enable 2FA on your Gmail account")
    print("   2. Generate an App Password (not your regular password)")
    print("   3. Set environment variables:")
    print("      export SMTP_EMAIL='your-email@gmail.com'")
    print("      export SMTP_PASSWORD='your-app-password'")
    print("\n   Or pass them to EmailService(smtp_email, smtp_password)")
    
    print("\n" + "=" * 70)
    print("✅ Email service ready!")