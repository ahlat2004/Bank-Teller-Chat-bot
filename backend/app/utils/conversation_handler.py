"""
Conversation Handler - Handles greetings and fallback intents
Provides quick responses for conversational patterns without invoking the ML model
"""

import re
from typing import Optional, Tuple, Dict, Any


class ConversationHandler:
    """
    Handles basic conversational patterns and greetings
    """
    
    # Greeting patterns
    GREETING_PATTERNS = {
        'hello': [r'\b(hello|hi|hey|hiya|howdy)\b', 'greeting'],
        'how_are_you': [r'\b(how are you|how are ya|how you doing|how\'s it going)\b', 'greeting'],
        'goodbye': [r'\b(bye|goodbye|see you|farewell|cya|take care|bye bye)\b', 'goodbye'],
        'thank_you': [r'\b(thank you|thanks|thankyou|thank|ta)\b', 'acknowledgement'],
        'help': [r'\b(help|assist|what can you do|what do you do|capabilities)\b', 'help_request'],
        'who_are_you': [r'\b(who are you|what are you|introduce yourself)\b', 'help_request'],
    }
    
    GREETING_RESPONSES = {
        'greeting': [
            "👋 Hello! I'm your Bank Teller Assistant. I can help you with banking services like checking balance, transfers, and account management. What would you like to do today?",
            "Hey there! 👋 Welcome to Bank Teller. How can I assist you with your banking needs?",
            "Hi! 👋 I'm here to help with your banking. What can I do for you?",
        ],
        'goodbye': [
            "Goodbye! 👋 Thank you for using Bank Teller. Have a great day!",
            "See you! 👋 Feel free to reach out anytime you need banking assistance.",
            "Bye! 👋 Thanks for using Bank Teller. Take care!",
        ],
        'acknowledgement': [
            "You're welcome! 😊 Is there anything else I can help you with?",
            "Happy to help! 😊 What else can I do for you?",
            "Anytime! 😊 What else do you need?",
        ],
        'help_request': [
            "I'm your AI Bank Teller Assistant! 🤖 I can help you with:\n"
            "• 💰 Check your account balance\n"
            "• 💸 Transfer money to other accounts\n"
            "• 📄 View transaction history\n"
            "• 🏦 Find ATMs and bank branches\n"
            "• 📱 Create a new account\n"
            "• 🔒 Block or activate cards\n"
            "• 💳 Apply for credit cards or loans\n\n"
            "What would you like to do?",
            "I'm your banking assistant! Here's what I can do:\n"
            "• Check balance\n"
            "• Transfer money\n"
            "• View transactions\n"
            "• Find ATMs/branches\n"
            "• Manage your accounts\n"
            "• Handle card operations\n\n"
            "What do you need help with?",
        ],
    }
    
    FALLBACK_RESPONSES = [
        "I'm not quite sure what you're asking. Could you rephrase that? I can help with balance checks, transfers, payments, and account management.",
        "I didn't quite understand. Could you be more specific? For example, you could say 'check balance' or 'transfer money'.",
        "I'm having trouble understanding. Please try rephrasing your request. What banking service do you need?",
    ]
    
    @staticmethod
    def detect_pattern(message: str) -> Optional[Tuple[str, str]]:
        """
        Detect conversational patterns in user message
        
        Args:
            message: User's message
            
        Returns:
            Tuple of (pattern_type, category) or None if no match
        """
        message_lower = message.lower().strip()
        
        # Check against all patterns
        for pattern_name, (pattern, category) in ConversationHandler.GREETING_PATTERNS.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                return (pattern_name, category)
        
        return None
    
    @staticmethod
    def get_response(pattern_type: str, category: str) -> str:
        """
        Get response for detected pattern
        
        Args:
            pattern_type: Type of pattern detected
            category: Category of response
            
        Returns:
            Response message
        """
        import random
        
        if category in ConversationHandler.GREETING_RESPONSES:
            return random.choice(ConversationHandler.GREETING_RESPONSES[category])
        
        return random.choice(ConversationHandler.FALLBACK_RESPONSES)
    
    @staticmethod
    def handle_greeting(message: str) -> Optional[Dict[str, Any]]:
        """
        Handle greeting/conversational message
        
        Args:
            message: User's message
            
        Returns:
            Response dict or None if not a greeting
        """
        pattern_info = ConversationHandler.detect_pattern(message)
        
        if pattern_info:
            pattern_type, category = pattern_info
            response = ConversationHandler.get_response(pattern_type, category)
            
            return {
                'response': response,
                'intent': pattern_type,
                'confidence': 0.99,
                'entities': {},
                'requires_input': True,
                'status': 'success',
                'is_greeting': True
            }
        
        return None
    
    @staticmethod
    def is_likely_casual(message: str) -> bool:
        """
        Check if message is likely casual/conversational
        
        Args:
            message: User's message
            
        Returns:
            True if message appears to be casual
        """
        message_lower = message.lower().strip()
        
        # Very short messages or single words are often casual
        if len(message_lower) < 10:
            return True
        
        # Messages with common casual patterns
        casual_indicators = [
            'hi ', 'hello', 'hey', 'bye', 'thanks', 'help', 'who are you',
            'what can you', 'what do you', 'how are you'
        ]
        
        for indicator in casual_indicators:
            if indicator in message_lower:
                return True
        
        return False


# Testing
if __name__ == "__main__":
    test_messages = [
        "hi",
        "Hello there!",
        "How are you doing?",
        "bye",
        "Thank you",
        "Who are you?",
        "I want to transfer money",
        "Check my balance",
    ]
    
    for msg in test_messages:
        result = ConversationHandler.handle_greeting(msg)
        print(f"\nMessage: '{msg}'")
        if result:
            print(f"✅ Greeting detected!")
            print(f"   Intent: {result['intent']}")
            print(f"   Response: {result['response'][:60]}...")
        else:
            print(f"❌ Not a greeting - needs intent classification")
