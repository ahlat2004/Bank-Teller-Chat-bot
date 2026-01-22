"""
Context Manager
Handles conversation context and entity resolution
"""

from typing import Dict, List, Optional, Any
import re


class ContextManager:
    """
    Manages conversation context for entity resolution
    Handles pronoun resolution, entity references, and context tracking
    """
    
    def __init__(self):
        """Initialize context manager"""
        self.conversation_context: Dict[str, Any] = {}
        self.entity_history: List[Dict[str, Any]] = []
        self.max_history_size = 5
        
        # Pronoun patterns for resolution
        self.pronoun_patterns = {
            'account': ['that account', 'the account', 'same account', 'this account', 'it'],
            'person': ['him', 'her', 'them', 'that person', 'the person'],
            'amount': ['that amount', 'the amount', 'same amount', 'that'],
            'general': ['this', 'that', 'same', 'it']
        }
    
    def update_context(self, entities: Dict[str, Any]):
        """
        Update conversation context with new entities
        
        Args:
            entities: New entities to add to context
        """
        # Store previous values before updating
        for key, value in entities.items():
            if value is not None:
                self.conversation_context[key] = value
        
        # Add to history
        self.entity_history.append(entities.copy())
        
        # Limit history size
        if len(self.entity_history) > self.max_history_size:
            self.entity_history.pop(0)
    
    def get_context_value(self, key: str) -> Optional[Any]:
        """
        Get value from current context
        
        Args:
            key: Context key to retrieve
            
        Returns:
            Value if exists, None otherwise
        """
        return self.conversation_context.get(key)
    
    def resolve_reference(self, text: str, entity_type: str) -> Optional[Any]:
        """
        Resolve pronoun/reference to previous entity
        
        Args:
            text: User message text
            entity_type: Type of entity to resolve (account, person, amount)
            
        Returns:
            Resolved entity value or None
        """
        text_lower = text.lower()
        
        # Check if text contains reference pattern
        patterns = self.pronoun_patterns.get(entity_type, [])
        
        for pattern in patterns:
            if pattern in text_lower:
                # Try to get from context
                value = self.get_context_value(entity_type)
                if value:
                    return value
        
        return None
    
    def resolve_entities_from_context(self, current_entities: Dict[str, Any], 
                                     user_message: str) -> Dict[str, Any]:
        """
        Resolve missing entities using context and references
        
        Args:
            current_entities: Currently extracted entities
            user_message: User's message text
            
        Returns:
            Enhanced entities dictionary
        """
        enhanced_entities = current_entities.copy()
        
        # Try to resolve missing entities
        if not enhanced_entities.get('amount'):
            resolved_amount = self.resolve_reference(user_message, 'amount')
            if resolved_amount:
                enhanced_entities['amount'] = resolved_amount
        
        if not enhanced_entities.get('account_number'):
            resolved_account = self.resolve_reference(user_message, 'account')
            if resolved_account:
                enhanced_entities['account_number'] = resolved_account
        
        if not enhanced_entities.get('person') and not enhanced_entities.get('payee'):
            resolved_person = self.resolve_reference(user_message, 'person')
            if resolved_person:
                enhanced_entities['person'] = resolved_person
                enhanced_entities['payee'] = resolved_person
        
        return enhanced_entities
    
    def get_last_entity(self, entity_type: str) -> Optional[Any]:
        """
        Get the most recent entity of given type from history
        
        Args:
            entity_type: Type of entity to retrieve
            
        Returns:
            Most recent entity value or None
        """
        # Search history in reverse (most recent first)
        for entities in reversed(self.entity_history):
            if entity_type in entities and entities[entity_type] is not None:
                return entities[entity_type]
        
        return None
    
    def has_context_for(self, entity_type: str) -> bool:
        """
        Check if context exists for given entity type
        
        Args:
            entity_type: Type of entity to check
            
        Returns:
            True if context exists
        """
        return entity_type in self.conversation_context
    
    def clear_context(self, entity_types: Optional[List[str]] = None):
        """
        Clear context for specific entity types or all
        
        Args:
            entity_types: List of entity types to clear, None for all
        """
        if entity_types is None:
            self.conversation_context.clear()
            self.entity_history.clear()
        else:
            for entity_type in entity_types:
                self.conversation_context.pop(entity_type, None)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get summary of current context
        
        Returns:
            Dictionary with context summary
        """
        return {
            'current_context': self.conversation_context.copy(),
            'history_size': len(self.entity_history),
            'available_entities': list(self.conversation_context.keys())
        }
    
    def detect_clarification_needed(self, current_entities: Dict[str, Any]) -> Optional[str]:
        """
        Detect if clarification is needed based on context
        
        Args:
            current_entities: Currently extracted entities
            
        Returns:
            Clarification question or None
        """
        # Check for ambiguous references
        text_indicators = current_entities.get('_original_text', '').lower()
        
        # Multiple accounts in context
        if 'account' in text_indicators and not current_entities.get('account_number'):
            # Check if user has multiple accounts in context
            if self.has_context_for('user_accounts'):
                accounts = self.get_context_value('user_accounts')
                if accounts and len(accounts) > 1:
                    return "Which account would you like to use?"
        
        # Ambiguous person reference
        if any(ref in text_indicators for ref in ['him', 'her', 'them', 'that person']):
            if not current_entities.get('person'):
                last_person = self.get_last_entity('person')
                if not last_person:
                    return "Who are you referring to?"
        
        return None
    
    def store_user_preferences(self, user_id: int, preferences: Dict[str, Any]):
        """
        Store user preferences in context
        
        Args:
            user_id: User identifier
            preferences: User preferences dictionary
        """
        self.conversation_context[f'user_{user_id}_prefs'] = preferences
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user preferences from context
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences or None
        """
        return self.conversation_context.get(f'user_{user_id}_prefs')
    
    def merge_with_history(self, current_entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge current entities with historical context
        
        Args:
            current_entities: Current extracted entities
            
        Returns:
            Merged entity dictionary
        """
        merged = {}
        
        # Start with historical context
        merged.update(self.conversation_context)
        
        # Override with current entities (current takes precedence)
        for key, value in current_entities.items():
            if value is not None:
                merged[key] = value
        
        return merged


# Example usage and tests
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "CONTEXT MANAGER TEST")
    print("=" * 70)
    
    context_mgr = ContextManager()
    
    # Scenario 1: First message
    print("\n📝 Scenario 1: Initial Transfer Request")
    print("-" * 70)
    
    entities_1 = {
        'amount': 5000.0,
        'payee': 'Ali Khan',
        'account_number': 'PK12ABCD1234567890123456'
    }
    
    context_mgr.update_context(entities_1)
    print(f"Updated context with: {entities_1}")
    print(f"Current context: {context_mgr.conversation_context}")
    
    # Scenario 2: Follow-up with pronoun reference
    print("\n📝 Scenario 2: Follow-up 'Send the same amount to Sarah'")
    print("-" * 70)
    
    entities_2 = {
        'payee': 'Sarah Ahmed'
    }
    
    # Try to resolve amount from context
    user_message_2 = "Send the same amount to Sarah"
    enhanced_entities_2 = context_mgr.resolve_entities_from_context(
        entities_2, user_message_2
    )
    
    print(f"Original entities: {entities_2}")
    print(f"Enhanced with context: {enhanced_entities_2}")
    
    # Scenario 3: Account reference
    print("\n📝 Scenario 3: 'Use that account again'")
    print("-" * 70)
    
    user_message_3 = "Use that account again"
    resolved_account = context_mgr.resolve_reference(user_message_3, 'account')
    print(f"Resolved account: {resolved_account}")
    
    # Scenario 4: History lookup
    print("\n📝 Scenario 4: Check Entity History")
    print("-" * 70)
    
    last_amount = context_mgr.get_last_entity('amount')
    last_payee = context_mgr.get_last_entity('payee')
    
    print(f"Last amount in history: {last_amount}")
    print(f"Last payee in history: {last_payee}")
    print(f"History size: {len(context_mgr.entity_history)}")
    
    # Scenario 5: Context summary
    print("\n📝 Scenario 5: Context Summary")
    print("-" * 70)
    
    summary = context_mgr.get_context_summary()
    print(f"Context summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✅ Context manager tests complete!")