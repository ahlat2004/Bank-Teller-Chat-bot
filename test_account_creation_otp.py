"""
Account Creation with OTP Integration Test
Tests the complete flow: name → phone → email → OTP → account type → confirmation
Target email: apexwolf993@gmail.com
"""

import requests
import json
import time
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
USER_ID = 1
TEST_EMAIL = "apexwolf993@gmail.com"
TEST_NAME = "Test User"
TEST_PHONE = "03001234567"
TEST_ACCOUNT_TYPE = "savings"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.END}\n")

def print_step(step_num, description):
    print(f"{Colors.BOLD}{Colors.CYAN}Step {step_num}: {description}{Colors.END}")
    print("-" * 80)

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def send_chat_message(message: str, session_id: Optional[str] = None) -> Dict[Any, Any]:
    """Send a message to the chat API"""
    payload = {
        "message": message,
        "user_id": USER_ID,
        "session_id": session_id
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to API. Make sure the server is running!")
        print_info(f"Start server with: uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    except requests.exceptions.RequestException as e:
        print_error(f"API Error: {e}")
        return None

def main():
    print_header("ACCOUNT CREATION WITH OTP VERIFICATION TEST")
    
    print_info(f"Test Configuration:")
    print_info(f"  • API URL: {API_BASE_URL}")
    print_info(f"  • Target Email: {TEST_EMAIL}")
    print_info(f"  • User Name: {TEST_NAME}")
    print_info(f"  • Phone: {TEST_PHONE}")
    print_info(f"  • Account Type: {TEST_ACCOUNT_TYPE}")
    
    session_id = None
    
    # Step 1: Initiate account creation
    print_step(1, "Initiate Account Creation")
    print(f"Sending: '{Colors.BOLD}I want to create a new account{Colors.END}'")
    
    response = send_chat_message("I want to create a new account")
    if not response:
        print_error("Failed to get response from API")
        return
    
    session_id = response.get('session_id')
    bot_response = response.get('response', '')
    
    print_success(f"Session created: {session_id}")
    print(f"\nBot: {Colors.BOLD}{bot_response}{Colors.END}\n")
    
    # Step 2: Provide name
    print_step(2, "Provide Full Name")
    print(f"Sending: '{Colors.BOLD}{TEST_NAME}{Colors.END}'")
    time.sleep(1)
    
    response = send_chat_message(TEST_NAME, session_id)
    if not response:
        print_error("Failed to get response")
        return
    
    bot_response = response.get('response', '')
    print_success("Name provided")
    print(f"Bot: {Colors.BOLD}{bot_response}{Colors.END}\n")
    
    # Step 3: Provide phone number
    print_step(3, "Provide Phone Number")
    print(f"Sending: '{Colors.BOLD}{TEST_PHONE}{Colors.END}'")
    time.sleep(1)
    
    response = send_chat_message(TEST_PHONE, session_id)
    if not response:
        print_error("Failed to get response")
        return
    
    bot_response = response.get('response', '')
    print_success("Phone number provided")
    print(f"Bot: {Colors.BOLD}{bot_response}{Colors.END}\n")
    
    # Step 4: Provide email (OTP will be sent)
    print_step(4, "Provide Email Address (OTP Will Be Sent)")
    print(f"Sending: '{Colors.BOLD}{TEST_EMAIL}{Colors.END}'")
    print_warning(f"📧 Watch for OTP email to arrive at {TEST_EMAIL}!")
    time.sleep(1)
    
    response = send_chat_message(TEST_EMAIL, session_id)
    if not response:
        print_error("Failed to get response")
        return
    
    bot_response = response.get('response', '')
    print_success("Email provided, OTP sent!")
    print(f"Bot: {Colors.BOLD}{bot_response}{Colors.END}\n")
    
    # Step 5: Wait for OTP and get it from user
    print_step(5, "Email Verification with OTP")
    print_warning(f"⏳ Check your email ({TEST_EMAIL}) for the OTP code...")
    print_info("The OTP is a 6-digit number. You have 5 minutes to use it.")
    
    # Get OTP from user
    otp_code = input(f"\n{Colors.BOLD}Enter the 6-digit OTP from your email: {Colors.END}").strip()
    
    if not otp_code or len(otp_code) != 6 or not otp_code.isdigit():
        print_error("Invalid OTP format. OTP must be 6 digits.")
        return
    
    print(f"Sending OTP: '{Colors.BOLD}{otp_code}{Colors.END}'")
    time.sleep(1)
    
    response = send_chat_message(otp_code, session_id)
    if not response:
        print_error("Failed to get response")
        return
    
    bot_response = response.get('response', '')
    
    # Check if OTP verification was successful
    if "verified" in bot_response.lower() or "email verified" in bot_response.lower():
        print_success("Email verified successfully!")
        print(f"Bot: {Colors.BOLD}{bot_response}{Colors.END}\n")
    else:
        print_error("OTP verification failed!")
        print(f"Bot response: {bot_response}")
        return
    
    # Step 6: Choose account type
    print_step(6, "Select Account Type")
    print(f"Sending: '{Colors.BOLD}{TEST_ACCOUNT_TYPE}{Colors.END}'")
    print_info("Available options: savings, current, salary")
    time.sleep(1)
    
    response = send_chat_message(TEST_ACCOUNT_TYPE, session_id)
    if not response:
        print_error("Failed to get response")
        return
    
    bot_response = response.get('response', '')
    print_success("Account type selected")
    print(f"Bot: {Colors.BOLD}{bot_response}{Colors.END}\n")
    
    # Step 7: Confirm account creation
    print_step(7, "Confirm Account Creation")
    print(f"Sending: '{Colors.BOLD}yes{Colors.END}'")
    time.sleep(1)
    
    response = send_chat_message("yes", session_id)
    if not response:
        print_error("Failed to get response")
        return
    
    bot_response = response.get('response', '')
    intent = response.get('intent', 'unknown')
    
    print_success("Confirmation sent")
    print(f"Bot: {Colors.BOLD}{bot_response}{Colors.END}\n")
    
    # Final summary
    print_header("ACCOUNT CREATION TEST COMPLETE! 🎉")
    
    if "account created" in bot_response.lower() or "successfully" in bot_response.lower():
        print_success("✅ ACCOUNT CREATION SUCCESSFUL!")
        print(f"\nFinal Response:\n{Colors.BOLD}{bot_response}{Colors.END}")
        print("\n" + "=" * 80)
        print(f"Session ID: {session_id}")
        print(f"User ID: {USER_ID}")
        print(f"Email: {TEST_EMAIL}")
        print("=" * 80)
    else:
        print_warning("Response indicates potential issues. Check the output above.")
        print(f"\nFinal Response:\n{Colors.BOLD}{bot_response}{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test cancelled by user.{Colors.END}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
