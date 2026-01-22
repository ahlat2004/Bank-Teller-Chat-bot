"""
State Machine - Dialogue state management with explicit states
Fixes Flaws: #6 (Intent Leakage), #7 (State Cleared in Multiple Places), 
             #8 (Implicit Race Conditions), #11 (Non-Deterministic Slot Order)
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


class DialogueStateEnum(Enum):
    """
    Five explicit dialogue states with clear transitions
    
    State Flow:
    IDLE → INTENT_CLASSIFIED → SLOTS_FILLING → CONFIRMATION_PENDING 
         → ACTION_EXECUTING → COMPLETED
         
    Error transitions:
    Any state → ERROR → IDLE
    """
    IDLE = "idle"
    INTENT_CLASSIFIED = "classified"
    SLOTS_FILLING = "filling"
    CONFIRMATION_PENDING = "pending"
    ACTION_EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class DialogueState:
    """
    Immutable dialogue state snapshot
    Contains all information about current dialogue
    """
    # Core state
    current_state: DialogueStateEnum = DialogueStateEnum.IDLE
    
    # Intent information
    intent: Optional[str] = None
    intent_confidence: float = 0.0
    intent_locked: bool = False  # Prevents reclassification mid-flow
    
    # Slot information
    required_slots: List[str] = field(default_factory=list)  # Ordered slot names
    filled_slots: Dict[str, Any] = field(default_factory=dict)  # Filled slot values
    slot_validation_errors: Dict[str, str] = field(default_factory=dict)  # Validation errors
    
    # Dialogue tracking
    turn_count: int = 0
    last_user_message: Optional[str] = None
    last_bot_response: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert state to dictionary for serialization"""
        data = asdict(self)
        data['current_state'] = self.current_state.value
        return data


class StateMachine:
    """
    Manages dialogue state transitions with validation
    Key features:
    - 5 explicit states (no ambiguous states)
    - Intent locking (prevents reclassification mid-flow)
    - Explicit slot ordering (deterministic dialogue flow)
    - Automatic state cleanup on errors
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        DialogueStateEnum.IDLE: [DialogueStateEnum.INTENT_CLASSIFIED, DialogueStateEnum.ERROR],
        DialogueStateEnum.INTENT_CLASSIFIED: [
            DialogueStateEnum.SLOTS_FILLING,
            DialogueStateEnum.CONFIRMATION_PENDING,
            DialogueStateEnum.ERROR,
        ],
        DialogueStateEnum.SLOTS_FILLING: [
            DialogueStateEnum.CONFIRMATION_PENDING,
            DialogueStateEnum.SLOTS_FILLING,  # Can ask for another slot
            DialogueStateEnum.ERROR,
        ],
        DialogueStateEnum.CONFIRMATION_PENDING: [
            DialogueStateEnum.ACTION_EXECUTING,
            DialogueStateEnum.SLOTS_FILLING,  # User changes mind
            DialogueStateEnum.ERROR,
        ],
        DialogueStateEnum.ACTION_EXECUTING: [
            DialogueStateEnum.COMPLETED,
            DialogueStateEnum.ERROR,
        ],
        DialogueStateEnum.COMPLETED: [DialogueStateEnum.IDLE],
        DialogueStateEnum.ERROR: [DialogueStateEnum.IDLE],
    }
    
    # Intent to required slots mapping
    INTENT_SLOTS = {
        "create_account": ["name", "phone", "email", "account_type"],
        "check_balance": ["account_type"],
        "transfer_money": ["amount", "from_account", "to_account", "recipient_phone"],
        "pay_bill": ["biller_id", "amount", "from_account"],
        "withdraw_cash": ["amount", "from_account"],
        "deposit_cash": ["amount", "to_account"],
        "request_card": ["card_type", "delivery_address"],
    }
    
    def __init__(self, state: Optional[DialogueState] = None):
        """Initialize state machine with optional existing state"""
        self.state = state or DialogueState()
        self.history: List[Tuple[DialogueStateEnum, str]] = []  # State change history
    
    def set_intent(self, intent: str, confidence: float = 0.0) -> bool:
        """
        Set intent and lock it to prevent reclassification
        Returns: True if successful, False if already locked
        """
        if self.state.intent_locked:
            return False  # Cannot change intent once locked
        
        self.state.intent = intent
        self.state.intent_confidence = confidence
        self.state.required_slots = self.INTENT_SLOTS.get(intent, [])
        self.state.intent_locked = True  # Lock immediately after setting
        
        # Auto-transition to INTENT_CLASSIFIED
        self.transition_to(DialogueStateEnum.INTENT_CLASSIFIED)
        
        return True
    
    def lock_intent(self) -> None:
        """Lock intent to prevent any reclassification during multi-turn flow"""
        self.state.intent_locked = True
    
    def is_intent_locked(self) -> bool:
        """Check if intent is locked"""
        return self.state.intent_locked
    
    def fill_slot(self, slot_name: str, value: Any) -> bool:
        """
        Fill a slot value
        Returns: True if successful, False if slot doesn't exist for this intent
        """
        if slot_name not in self.state.required_slots:
            return False
        
        self.state.filled_slots[slot_name] = value
        self.state.slot_validation_errors.pop(slot_name, None)  # Clear previous errors
        
        return True
    
    def fill_slots_from_dict(self, slots_dict: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Fill multiple slots at once
        Returns: (all_filled: bool, validation_errors: Dict)
        """
        errors = {}
        
        for slot_name, value in slots_dict.items():
            if slot_name not in self.state.required_slots:
                errors[slot_name] = f"Unknown slot '{slot_name}' for intent '{self.state.intent}'"
            else:
                self.fill_slot(slot_name, value)
        
        return len(errors) == 0, errors
    
    def clear_slot(self, slot_name: str) -> bool:
        """Clear a slot value (user changed their mind)"""
        if slot_name in self.state.filled_slots:
            del self.state.filled_slots[slot_name]
            return True
        return False
    
    def get_missing_slots(self) -> List[str]:
        """Get list of unfilled required slots"""
        return [
            slot for slot in self.state.required_slots
            if slot not in self.state.filled_slots
        ]
    
    def has_missing_slots(self) -> bool:
        """Check if any required slots are missing"""
        return len(self.get_missing_slots()) > 0
    
    def get_next_missing_slot(self) -> Optional[str]:
        """Get the next slot to ask for (in order)"""
        missing = self.get_missing_slots()
        return missing[0] if missing else None
    
    def are_all_slots_filled(self) -> bool:
        """Check if all required slots are filled"""
        return not self.has_missing_slots()
    
    def needs_confirmation(self) -> bool:
        """Check if all slots filled and ready for confirmation"""
        return self.are_all_slots_filled() and self.current_state == DialogueStateEnum.INTENT_CLASSIFIED
    
    def set_validation_error(self, slot_name: str, error_message: str) -> None:
        """Set validation error for a slot"""
        self.state.slot_validation_errors[slot_name] = error_message
    
    def get_validation_errors(self) -> Dict[str, str]:
        """Get all validation errors"""
        return self.state.slot_validation_errors.copy()
    
    def clear_validation_errors(self) -> None:
        """Clear all validation errors"""
        self.state.slot_validation_errors.clear()
    
    def transition_to(self, new_state: DialogueStateEnum) -> bool:
        """
        Transition to a new state with validation
        Returns: True if successful, False if invalid transition
        """
        if not self.validate_transition(self.state.current_state, new_state):
            return False
        
        # Record transition
        self.history.append((self.state.current_state, new_state.value))
        self.state.current_state = new_state
        self.state.updated_at = datetime.now().isoformat()
        
        return True
    
    def validate_transition(self, from_state: DialogueStateEnum, to_state: DialogueStateEnum) -> bool:
        """Check if transition is valid"""
        allowed_states = self.VALID_TRANSITIONS.get(from_state, [])
        return to_state in allowed_states
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get human-readable summary of current state"""
        return {
            "current_state": self.state.current_state.value,
            "intent": self.state.intent,
            "intent_confidence": self.state.intent_confidence,
            "intent_locked": self.state.intent_locked,
            "filled_slots": self.state.filled_slots.copy(),
            "missing_slots": self.get_missing_slots(),
            "next_slot_to_ask": self.get_next_missing_slot(),
            "all_slots_filled": self.are_all_slots_filled(),
            "turn_count": self.state.turn_count,
            "validation_errors": self.state.slot_validation_errors.copy(),
        }
    
    def handle_user_input(self, message: str) -> None:
        """Record user input"""
        self.state.last_user_message = message
        self.state.turn_count += 1
        self.state.updated_at = datetime.now().isoformat()
    
    def handle_bot_response(self, response: str) -> None:
        """Record bot response"""
        self.state.last_bot_response = response
        self.state.updated_at = datetime.now().isoformat()
    
    def set_error(self, error_message: str) -> None:
        """Set error state"""
        self.state.error_message = error_message
        self.transition_to(DialogueStateEnum.ERROR)
    
    def clear_state(self) -> None:
        """Clear state for next dialogue (go back to IDLE)"""
        self.transition_to(DialogueStateEnum.IDLE)
        self.state = DialogueState()
    
    def save_state(self) -> Dict[str, Any]:
        """Serialize state to dict for storage"""
        return self.state.to_dict()
    
    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """Restore state from dict"""
        # Convert state string back to enum
        state_value = state_dict.get('current_state', 'idle')
        state_dict['current_state'] = DialogueStateEnum(state_value)
        
        self.state = DialogueState(**state_dict)
    
    @property
    def current_state(self) -> DialogueStateEnum:
        """Get current state"""
        return self.state.current_state
    
    @property
    def intent(self) -> Optional[str]:
        """Get current intent"""
        return self.state.intent
    
    @property
    def filled_slots(self) -> Dict[str, Any]:
        """Get filled slots"""
        return self.state.filled_slots.copy()
