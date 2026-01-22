"""
Authentication Module
Handles email OTP verification
Place in: backend/app/auth/__init__.py
"""

from auth.email_service import EmailService
from auth.otp_manager import OTPManager
from auth.auth_manager import AuthManager

__all__ = [
    'EmailService',
    'OTPManager',
    'AuthManager'
]