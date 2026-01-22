"""
Dialogue State Management
Maintains conversation state across multiple turns
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class ConversationStatus(Enum):
    """Conversation status enumeration"""
    ACTIVE = "active"
    WAITING_INPUT = "waiting_input"
    CONFIRMATION_PENDING = "confirmation_pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class DialogueState:
    """
    Maintains state of a conversation
    Tracks intent, entities, required slots, and conversation flow
    """
    
    def __init__(self, user_id: int, session_id: str):
        """
        Initialize dialogue state
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        self.user_id = user_id
        self.session_id = session_id
        
        # Intent and confidence
        self.intent: Optional[str] = None
        self.intent_confidence: float = 0.0
        
        # Entity tracking
        self.entities: Dict[str, Any] = {}
        self.required_slots: List[str] = []
        self.filled_slots: Dict[str, Any] = {}
        self.missing_slots: List[str] = []
        
        # Conversation flow
        self.status: ConversationStatus = ConversationStatus.ACTIVE
        self.turn_count: int = 0
        self.max_turns: int = 10
        
        # Confirmation
        self.confirmation_pending: bool = False
        self.pending_action: Optional[Dict[str, Any]] = None
        
        # Context and history
        self.context: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, str]] = []
        
        # Timestamps
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
    
    def set_intent(self, intent: str, confidence: float):
        """
        Set the conversation intent
        
        Args:
            intent: Intent name
            confidence: Confidence score (0-1)
        """
        self.intent = intent
        self.intent_confidence = confidence
        self.last_updated = datetime.now()
    
    def add_entities(self, entities: Dict[str, Any]):
        """
        Add extracted entities to state
        
        Args:
            entities: Dictionary of entities
        """
        self.entities.update(entities)
        self.last_updated = datetime.now()
    
    def set_required_slots(self, slots: List[str]):
        """
        Set required slots for current intent
        
        Args:
            slots: List of required slot names
        """
        self.required_slots = slots
        self.update_slot_status()
    
    def fill_slot(self, slot_name: str, value: Any):
        """
        Fill a specific slot with value
        
        Args:
            slot_name: Name of slot to fill
            value: Value to assign
        """
        self.filled_slots[slot_name] = value
        self.update_slot_status()
        self.last_updated = datetime.now()
    
    def update_slot_status(self):
        """Update missing slots list based on required and filled slots"""
        self.missing_slots = [
            slot for slot in self.required_slots 
            if slot not in self.filled_slots or self.filled_slots[slot] is None
        ]
    
    def is_complete(self) -> bool:
        """
        Check if all required slots are filled
        
        Returns:
            bool: True if all slots filled or no slots required
        """
        # If no required slots, dialogue is complete immediately
        if len(self.required_slots) == 0:
            return True
        # Otherwise check if all required slots are filled
        return len(self.missing_slots) == 0
    
    def set_confirmation_pending(self, action: Dict[str, Any]):
        """
        Set confirmation as pending
        
        Args:
            action: Action details awaiting confirmation
        """
        self.confirmation_pending = True
        self.pending_action = action
        self.status = ConversationStatus.CONFIRMATION_PENDING
        self.last_updated = datetime.now()
    
    def confirm_action(self):
        """Confirm the pending action"""
        self.confirmation_pending = False
        self.status = ConversationStatus.COMPLETED
        self.last_updated = datetime.now()
    
    def cancel_action(self):
        """Cancel the pending action"""
        self.confirmation_pending = False
        self.pending_action = None
        self.status = ConversationStatus.CANCELLED
        self.last_updated = datetime.now()
    
    def increment_turn(self):
        """Increment conversation turn counter"""
        self.turn_count += 1
        self.last_updated = datetime.now()
        
        # Check if max turns exceeded
        if self.turn_count >= self.max_turns:
            self.status = ConversationStatus.FAILED
    
    def add_to_history(self, role: str, message: str):
        """
        Add message to conversation history
        
        Args:
            role: 'user' or 'assistant'
            message: Message text
        """
        self.conversation_history.append({
            'role': role,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_context_value(self, key: str, default: Any = None) -> Any:
        """
        Get value from context
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Context value or default
        """
        return self.context.get(key, default)
    
    def set_context_value(self, key: str, value: Any):
        """
        Set context value
        
        Args:
            key: Context key
            value: Value to store
        """
        self.context[key] = value
        self.last_updated = datetime.now()
    
    def reset(self):
        """Reset state for new conversation"""
        self.intent = None
        self.intent_confidence = 0.0
        self.entities = {}
        self.required_slots = []
        self.filled_slots = {}
        self.missing_slots = []
        self.status = ConversationStatus.ACTIVE
        self.confirmation_pending = False
        self.pending_action = None
        self.turn_count = 0
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary for serialization
        
        Returns:
            Dictionary representation of state
        """
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'intent': self.intent,
            'intent_confidence': self.intent_confidence,
            'entities': self.entities,
            'required_slots': self.required_slots,
            'filled_slots': self.filled_slots,
            'missing_slots': self.missing_slots,
            'status': self.status.value,
            'turn_count': self.turn_count,
            'confirmation_pending': self.confirmation_pending,
            'pending_action': self.pending_action,
            'context': self.context,
            'conversation_history': self.conversation_history,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueState':
        """
        Create DialogueState from dictionary
        
        Args:
            data: Dictionary representation
            
        Returns:
            DialogueState instance
        """
        state = cls(data['user_id'], data['session_id'])
        state.intent = data.get('intent')
        state.intent_confidence = data.get('intent_confidence', 0.0)
        state.entities = data.get('entities', {})
        state.required_slots = data.get('required_slots', [])
        state.filled_slots = data.get('filled_slots', {})
        state.missing_slots = data.get('missing_slots', [])
        state.status = ConversationStatus(data.get('status', 'active'))
        state.turn_count = data.get('turn_count', 0)
        state.confirmation_pending = data.get('confirmation_pending', False)
        state.pending_action = data.get('pending_action')
        state.context = data.get('context', {})
        state.conversation_history = data.get('conversation_history', [])
        
        return state
    
    def __repr__(self) -> str:
        """String representation of dialogue state"""
        return (
            f"DialogueState(session={self.session_id}, "
            f"intent={self.intent}, "
            f"status={self.status.value}, "
            f"turns={self.turn_count}, "
            f"slots={len(self.filled_slots)}/{len(self.required_slots)})"
        )


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "DIALOGUE STATE TEST")
    print("=" * 70)
    
    # Create new state
    state = DialogueState(user_id=1, session_id="test_123")
    print(f"\n✅ Created: {state}")
    
    # Set intent
    state.set_intent("transfer_money", confidence=0.95)
    print(f"✅ Intent set: {state.intent} (confidence: {state.intent_confidence})")
    
    # Define required slots
    state.set_required_slots(['amount', 'payee', 'source_account'])
    print(f"✅ Required slots: {state.required_slots}")
    print(f"   Missing slots: {state.missing_slots}")
    
    # Fill slots progressively
    state.fill_slot('amount', 5000.0)
    print(f"\n✅ Filled 'amount': {state.filled_slots['amount']}")
    print(f"   Missing slots: {state.missing_slots}")
    
    state.fill_slot('payee', 'Ali Khan')
    print(f"\n✅ Filled 'payee': {state.filled_slots['payee']}")
    print(f"   Missing slots: {state.missing_slots}")
    
    state.fill_slot('source_account', 'PK12ABCD1234567890123456')
    print(f"\n✅ Filled 'source_account': {state.filled_slots['source_account']}")
    print(f"   Missing slots: {state.missing_slots}")
    
    # Check completion
    print(f"\n✅ Is complete: {state.is_complete()}")
    
    # Test confirmation
    state.set_confirmation_pending({
        'action': 'transfer',
        'amount': 5000.0,
        'payee': 'Ali Khan'
    })
    print(f"\n✅ Confirmation pending: {state.confirmation_pending}")
    print(f"   Status: {state.status.value}")
    
    # Convert to dict
    state_dict = state.to_dict()
    print(f"\n✅ Serialized to dict: {len(state_dict)} keys")
    
    print("\n" + "=" * 70)
    print("✅ Dialogue state tests complete!")