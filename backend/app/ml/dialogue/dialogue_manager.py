"""
Dialogue Manager
Orchestrates conversation flow, slot filling, and response generation
"""

from typing import Dict, List, Optional, Any, Tuple
import random

from .dialogue_state import DialogueState, ConversationStatus
from .context_manager import ContextManager


class DialogueManager:
    """
    Main dialogue management system
    Handles slot filling, multi-turn conversations, and confirmations
    """
    
    def __init__(self):
        """Initialize dialogue manager"""
        self.context_manager = ContextManager()
        
        # Define slot requirements for each intent
        # Empty list means intent is immediately complete (no slots required)
        self.intent_slots = {
            'transfer_money': ['amount', 'payee', 'source_account'],
            'check_balance': [],  # No required slots - show default account if none specified
            'bill_payment': ['bill_type', 'amount'],
            'transaction_history': [],  # No required slots - show default account history
            'block_card': ['card_number'],
            'apply_credit_card': ['card_type'],
            'update_phone': ['phone_number'],
            'report_fraud': ['description'],
            'create_account': ['name', 'phone', 'email', 'otp_code', 'account_type'],
        }
        
        # Slot prompts for missing information
        self.slot_prompts = {
            'amount': [
                "How much would you like to transfer?",
                "What amount should I transfer?",
                "Please specify the amount."
            ],
            'payee': [
                "Who would you like to send money to?",
                "Who is the recipient?",
                "Please provide the payee's name."
            ],
            'source_account': [
                "Which account should I use?",
                "From which account?",
                "Please specify the source account."
            ],
            'account_number': [
                "Which account would you like to check?",
                "Please provide your account number.",
                "Which account?"
            ],
            'bill_type': [
                "Which bill would you like to pay?",
                "What type of bill is this?",
                "Please specify the bill type (electricity, mobile, gas, etc.)."
            ],
            'phone_number': [
                "What's your new phone number?",
                "Please provide your phone number.",
                "What phone number?"
            ],
            'card_type': [
                "Which type of credit card? (Gold, Platinum, or Business)",
                "What card type would you like?",
                "Please specify the card type."
            ],
            'name': [
                "What's your full name?",
                "Please provide your name.",
                "Your name?"
            ],
            'phone': [
                "What's your phone number? (Format: 03XXXXXXXXX)",
                "Please provide your mobile number.",
                "Your phone number?"
            ],
            'email': [
                "What's your email address?",
                "Please provide your email for verification.",
                "Your email?"
            ],
            'otp_code': [
                "Please enter the 6-digit verification code sent to your email.",
                "Enter the OTP code from your email.",
                "Verification code?"
            ],
            'account_type': [
                "What type of account would you like? (savings/current/salary)",
                "Choose account type: savings, current, or salary",
                "Account type?"
            ]
        }
        
        # Confirmation templates
        self.confirmation_templates = {
            'transfer_money': "Please confirm: Transfer PKR {amount:,.2f} to {payee}?",
            'bill_payment': "Please confirm: Pay {bill_type} bill of PKR {amount:,.2f}?",
            'block_card': "Please confirm: Block card ending in {card_number}?",
        }
        
        # Fallback responses
        self.fallback_responses = [
            "I didn't quite understand that. Could you please rephrase?",
            "I'm not sure I understood. Can you provide more details?",
            "Could you clarify what you'd like to do?",
        ]
        
        # Yes/No patterns for confirmation
        self.yes_patterns = ['yes', 'yeah', 'yep', 'confirm', 'proceed', 'ok', 'okay', 'correct', 'right']
        self.no_patterns = ['no', 'nope', 'cancel', 'stop', 'nevermind', 'don\'t']
    
    def process_turn(self, state: DialogueState, 
                    user_message: str,
                    intent: str,
                    intent_confidence: float,
                    entities: Dict[str, Any]) -> Tuple[str, DialogueState]:
        """
        Process a conversation turn
        
        Args:
            state: Current dialogue state
            user_message: User's message
            intent: Predicted intent
            intent_confidence: Intent confidence score
            entities: Extracted entities
            
        Returns:
            Tuple of (response_message, updated_state)
        """
        # Increment turn counter
        state.increment_turn()
        
        # Add to conversation history
        state.add_to_history('user', user_message)
        
        # Check if waiting for confirmation
        if state.confirmation_pending:
            response = self._handle_confirmation(state, user_message)
            state.add_to_history('assistant', response)
            return response, state
        
        # Check for low confidence
        if intent_confidence < 0.6:
            response = self._handle_low_confidence(state, user_message)
            state.add_to_history('assistant', response)
            return response, state
        
        # Set intent if new or changed
        if state.intent != intent:
            state.set_intent(intent, intent_confidence)
            
            # Set required slots for this intent
            required_slots = self.intent_slots.get(intent, [])
            state.set_required_slots(required_slots)
        
        # Update entities with context resolution
        enhanced_entities = self.context_manager.resolve_entities_from_context(
            entities, user_message
        )
        
        # Update context
        self.context_manager.update_context(enhanced_entities)
        
        # Fill slots from entities
        self._fill_slots_from_entities(state, enhanced_entities)
        
        # Check if all slots are filled
        if state.is_complete():
            response = self._handle_complete_slots(state)
        else:
            response = self._ask_for_missing_slot(state)
        
        state.add_to_history('assistant', response)
        return response, state
    
    def _fill_slots_from_entities(self, state: DialogueState, entities: Dict[str, Any]):
        """
        Fill dialogue slots from extracted entities
        
        Args:
            state: Current dialogue state
            entities: Extracted entities
        """
        for slot in state.required_slots:
            # Map entity names to slot names
            entity_value = None
            
            if slot == 'amount':
                entity_value = entities.get('amount')
            elif slot == 'payee':
                entity_value = entities.get('payee') or entities.get('person')
            elif slot == 'source_account' or slot == 'account_number':
                entity_value = entities.get('account_number')
            elif slot == 'bill_type':
                entity_value = entities.get('bill_type')
            elif slot == 'phone_number' or slot == 'phone':
                entity_value = entities.get('phone_number')
            elif slot == 'card_number':
                entity_value = entities.get('card_number')
            elif slot == 'card_type':
                entity_value = entities.get('card_type')
            elif slot == 'name':
                entity_value = entities.get('person')
            elif slot == 'email':
                # Email won't be in entities, user must type it
                pass
            elif slot == 'otp_code':
                # OTP won't be in entities, user must type it
                pass
            elif slot == 'account_type':
                # Account type might be mentioned
                pass
            
            # Fill slot if value found and not already filled
            if entity_value and slot not in state.filled_slots:
                state.fill_slot(slot, entity_value)
    
    def _ask_for_missing_slot(self, state: DialogueState) -> str:
        """
        Generate prompt for the first missing slot
        
        Args:
            state: Current dialogue state
            
        Returns:
            Prompt message
        """
        if not state.missing_slots:
            return "I have all the information I need."
        
        # Get first missing slot
        missing_slot = state.missing_slots[0]
        
        # Get random prompt for this slot
        prompts = self.slot_prompts.get(missing_slot, [f"Please provide {missing_slot}."])
        prompt = random.choice(prompts)
        
        return prompt
    
    def _handle_complete_slots(self, state: DialogueState) -> str:
        """
        Handle case when all slots are filled
        
        Args:
            state: Current dialogue state
            
        Returns:
            Confirmation message
        """
        intent = state.intent
        
        # Check if this intent requires confirmation
        if intent in self.confirmation_templates:
            confirmation_msg = self._generate_confirmation(state)
            
            # Set pending action
            state.set_confirmation_pending({
                'intent': intent,
                'slots': state.filled_slots.copy()
            })
            
            return confirmation_msg
        else:
            # No confirmation needed, execute directly
            return self._generate_success_message(state)
    
    def _generate_confirmation(self, state: DialogueState) -> str:
        """
        Generate confirmation message
        
        Args:
            state: Current dialogue state
            
        Returns:
            Confirmation message
        """
        template = self.confirmation_templates.get(state.intent, 
                                                   "Please confirm this action: {action}")
        
        try:
            message = template.format(**state.filled_slots)
            return f"{message} (yes/no)"
        except KeyError:
            return f"Please confirm: {state.intent} with the provided information. (yes/no)"
    
    def _handle_confirmation(self, state: DialogueState, user_message: str) -> str:
        """
        Handle user's confirmation response
        
        Args:
            state: Current dialogue state
            user_message: User's response
            
        Returns:
            Response message
        """
        user_message_lower = user_message.lower()
        
        # Check for yes
        if any(pattern in user_message_lower for pattern in self.yes_patterns):
            state.confirm_action()
            return self._generate_success_message(state)
        
        # Check for no
        elif any(pattern in user_message_lower for pattern in self.no_patterns):
            state.cancel_action()
            return "Okay, I've cancelled that action. Is there anything else I can help you with?"
        
        # Unclear response
        else:
            return "Please reply with 'yes' to confirm or 'no' to cancel."
    
    def _generate_success_message(self, state: DialogueState) -> str:
        """
        Generate success message after action completion
        
        Args:
            state: Current dialogue state
            
        Returns:
            Success message
        """
        intent = state.intent
        slots = state.filled_slots
        
        messages = {
            'transfer_money': f"✅ Successfully transferred PKR {slots.get('amount', 0):,.2f} to {slots.get('payee', 'recipient')}.",
            'bill_payment': f"✅ Successfully paid {slots.get('bill_type', 'your')} bill of PKR {slots.get('amount', 0):,.2f}.",
            'check_balance': f"Your account balance is PKR 25,450.00",  # Will be replaced with actual DB query
            'transaction_history': f"Here are your recent transactions...",
            'block_card': f"✅ Your card has been blocked successfully.",
            'create_account': f"✅ {slots.get('account_type', 'account').capitalize()} account created successfully!",
        }
        
        return messages.get(intent, f"✅ Action completed successfully.")
    
    def _handle_low_confidence(self, state: DialogueState, user_message: str) -> str:
        """
        Handle low confidence intent predictions
        
        Args:
            state: Current dialogue state
            user_message: User's message
            
        Returns:
            Fallback response
        """
        # Increment fallback counter
        fallback_count = state.get_context_value('fallback_count', 0) + 1
        state.set_context_value('fallback_count', fallback_count)
        
        # After 2 failed attempts, offer help
        if fallback_count >= 2:
            return ("I'm having trouble understanding. I can help you with:\n"
                   "• Check balance\n"
                   "• Transfer money\n"
                   "• Pay bills\n"
                   "• View transaction history\n"
                   "What would you like to do?")
        
        return random.choice(self.fallback_responses)
    
    def reset_session(self, state: DialogueState):
        """
        Reset session state
        
        Args:
            state: Dialogue state to reset
        """
        state.reset()
        self.context_manager.clear_context()


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 15 + "DIALOGUE MANAGER TEST")
    print("=" * 70)
    
    # Create dialogue manager and state
    dm = DialogueManager()
    state = DialogueState(user_id=1, session_id="test_123")
    
    # Scenario 1: Transfer Money - Complete in one turn
    print("\n📝 Scenario 1: Complete Transfer Request")
    print("-" * 70)
    
    user_msg_1 = "Transfer PKR 5000 to Ali Khan"
    intent_1 = "transfer_money"
    confidence_1 = 0.95
    entities_1 = {'amount': 5000.0, 'payee': 'Ali Khan'}
    
    response_1, state = dm.process_turn(state, user_msg_1, intent_1, confidence_1, entities_1)
    print(f"User: {user_msg_1}")
    print(f"Bot: {response_1}")
    
    # Scenario 2: Multi-turn Transfer - Missing account
    print("\n📝 Scenario 2: Multi-turn Transfer (Missing Account)")
    print("-" * 70)
    
    state2 = DialogueState(user_id=1, session_id="test_234")
    user_msg_2a = "Transfer 10000 to Sarah"
    entities_2a = {'amount': 10000.0, 'payee': 'Sarah'}
    
    response_2a, state2 = dm.process_turn(state2, user_msg_2a, "transfer_money", 0.92, entities_2a)
    print(f"User: {user_msg_2a}")
    print(f"Bot: {response_2a}")
    
    # User provides account
    user_msg_2b = "Use my savings account"
    entities_2b = {'account_number': 'PK12ABCD1234567890123456'}
    
    response_2b, state2 = dm.process_turn(state2, user_msg_2b, "transfer_money", 0.90, entities_2b)
    print(f"User: {user_msg_2b}")
    print(f"Bot: {response_2b}")
    
    # Scenario 3: Confirmation
    print("\n📝 Scenario 3: Confirmation Flow")
    print("-" * 70)
    
    # User confirms
    user_msg_2c = "yes"
    response_2c, state2 = dm.process_turn(state2, user_msg_2c, "", 0.0, {})
    print(f"User: {user_msg_2c}")
    print(f"Bot: {response_2c}")
    
    # Scenario 4: Low Confidence
    print("\n📝 Scenario 4: Low Confidence Handling")
    print("-" * 70)
    
    state3 = DialogueState(user_id=1, session_id="test_345")
    user_msg_3 = "I want to do something with my money"
    response_3, state3 = dm.process_turn(state3, user_msg_3, "unknown", 0.3, {})
    print(f"User: {user_msg_3}")
    print(f"Bot: {response_3}")
    
    print("\n" + "=" * 70)
    print("✅ Dialogue manager tests complete!")
