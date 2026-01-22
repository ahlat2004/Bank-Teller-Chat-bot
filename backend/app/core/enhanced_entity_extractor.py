"""
Phase 4: Enhanced Entity Extractor
Adds domain-aware banking patterns, implicit amounts, and negation detection
Fixes Flaws: #9 (Implicit Amounts), #10 (Negation Handling)
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class NegationScope(Enum):
    """Scope of negation in banking context"""
    ACCOUNT_TYPE = "account_type"
    AMOUNT = "amount"
    ACTION = "action"
    BROAD = "broad"


class EnhancedBankingEntityExtractor:
    """
    Enhanced entity extractor with:
    - Implicit amount handling ("send all my money")
    - Negation detection ("don't use savings")
    - Domain-aware banking patterns
    - Account type inference
    """
    
    # Implicit amount patterns
    IMPLICIT_AMOUNT_PATTERNS = {
        r'\ball\b.*\bmoney\b|\bsend\s+all\b|\btransfer\s+all\b': 'all',
        r'\bremainin[g]?\b.*\bamount\b|\bremainin[g]?\b': 'remaining',
        r'\beverything\b': 'all',
        r'\bentire\b.*\b(balance|amount)\b': 'all',
        r'\bmaximum\b|\bmax\b': 'max',
        r'\bhalf\b': 'half',
    }
    
    # Negation patterns with scope detection
    NEGATION_PATTERNS = {
        r"don't\s+use\s+(\w+)": NegationScope.ACCOUNT_TYPE,
        r"not\s+from\s+(\w+)": NegationScope.ACCOUNT_TYPE,
        r"don't\s+send\s+from\s+(\w+)": NegationScope.ACCOUNT_TYPE,
        r"exclude\s+(\w+)": NegationScope.ACCOUNT_TYPE,
        r"not\s+(\d+)": NegationScope.AMOUNT,
        r"less\s+than\s+(\d+)": NegationScope.AMOUNT,
    }
    
    # Account type patterns
    ACCOUNT_TYPE_PATTERNS = {
        r'\bsalary\b': 'salary',
        r'\bsavings\b|\bsave\b': 'savings',
        r'\bcurrent\b': 'current',
        r'\bcheckings?\b': 'current',
    }
    
    # Biller patterns for bill payments
    BILLER_PATTERNS = {
        r'\belectric\w*\b|\bpower\b|\butility\b': 'electricity',
        r'\bwater\b': 'water',
        r'\bgas\b': 'gas',
        r'\bphone\b|\bmobile\b': 'phone',
        r'\binternet\b|\bbroad\b': 'internet',
        r'\brent\b': 'rent',
        r'\bschool\b|\btuition\b|\bfees\b': 'education',
        r'\binsurance\b': 'insurance',
    }
    
    def __init__(self):
        """Initialize enhanced entity extractor"""
        self.negations_found = {}
    
    def extract_implicit_amounts(self, message: str) -> Optional[str]:
        """
        Extract implicit amount like 'all', 'remaining', 'max', 'half'
        
        Args:
            message: User message
        
        Returns:
            'all', 'remaining', 'max', 'half', or None
        """
        message_lower = message.lower()
        
        for pattern, amount_type in self.IMPLICIT_AMOUNT_PATTERNS.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                return amount_type
        
        return None
    
    def detect_negation(self, message: str) -> Tuple[bool, Optional[NegationScope], Optional[str]]:
        """
        Detect negation patterns and extract the negated entity
        
        Args:
            message: User message
        
        Returns:
            Tuple of (has_negation, scope, entity_name)
            Example: (True, NegationScope.ACCOUNT_TYPE, 'savings')
        """
        message_lower = message.lower()
        
        for pattern, scope in self.NEGATION_PATTERNS.items():
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                entity = match.group(1) if match.groups() else None
                return True, scope, entity
        
        return False, None, None
    
    def infer_account_type(self, message: str) -> Optional[str]:
        """
        Infer account type from message context
        
        Args:
            message: User message
        
        Returns:
            'salary', 'savings', or 'current', or None
        """
        message_lower = message.lower()
        
        for pattern, account_type in self.ACCOUNT_TYPE_PATTERNS.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                return account_type
        
        return None
    
    def infer_biller(self, message: str) -> Optional[str]:
        """
        Infer biller type from message
        
        Args:
            message: User message
        
        Returns:
            Biller name ('electricity', 'water', 'phone', etc.) or None
        """
        message_lower = message.lower()
        
        for pattern, biller in self.BILLER_PATTERNS.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                return biller
        
        return None
    
    def extract_amount_with_negation(self, message: str) -> Dict[str, Any]:
        """
        Extract amount handling both explicit and negated amounts
        
        Args:
            message: User message
        
        Returns:
            Dict with amount info including negation if present
        """
        # Check for negation first
        has_negation, scope, entity = self.detect_negation(message)
        
        result = {
            'has_negation': has_negation,
            'negation_scope': scope,
            'negated_entity': entity,
            'implicit_amount': self.extract_implicit_amounts(message)
        }
        
        return result
    
    def extract_context_aware_entities(self, message: str, intent: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract entities aware of intent context
        
        Args:
            message: User message
            intent: Current intent (for context-aware extraction)
        
        Returns:
            Dict of extracted entities with context awareness
        """
        entities = {}
        
        # Account type (relevant for most intents)
        account_type = self.infer_account_type(message)
        if account_type:
            entities['account_type'] = account_type
        
        # Implicit amounts (relevant for transfer, payment)
        implicit_amount = self.extract_implicit_amounts(message)
        if implicit_amount:
            entities['implicit_amount'] = implicit_amount
        
        # Negation detection (relevant for all intents)
        has_negation, scope, negated_entity = self.detect_negation(message)
        if has_negation:
            entities['negation'] = {
                'present': True,
                'scope': scope.value if scope else None,
                'entity': negated_entity
            }
        
        # Biller (relevant for bill_payment)
        if intent == 'bill_payment':
            biller = self.infer_biller(message)
            if biller:
                entities['biller'] = biller
        
        return entities
    
    def validate_negation_compatibility(self, intent: str, negation: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate if negation makes sense for the intent
        
        Args:
            intent: Current intent
            negation: Negation dict from detect_negation
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not negation.get('present'):
            return True, ""
        
        scope = negation.get('scope')
        
        # Transfer: can negate account type
        if intent == 'transfer_money':
            if scope in ['account_type']:
                return True, ""
            else:
                return False, "You can use 'don't use [account]' to exclude an account from the transfer"
        
        # Create account: negation doesn't make sense
        if intent == 'create_account':
            return False, "You can't use negation when creating an account"
        
        # Check balance: can negate account type
        if intent == 'check_balance':
            if scope in ['account_type']:
                return True, ""
        
        # Default: allow negation
        return True, ""
    
    def resolve_implicit_to_explicit(self, implicit_amount: str, available_balance: float) -> float:
        """
        Convert implicit amount ('all', 'remaining') to explicit amount
        
        Args:
            implicit_amount: 'all', 'remaining', 'max', 'half'
            available_balance: Available balance in account
        
        Returns:
            Explicit amount as float
        """
        if implicit_amount == 'all' or implicit_amount == 'remaining':
            return available_balance
        elif implicit_amount == 'max':
            return available_balance
        elif implicit_amount == 'half':
            return available_balance / 2
        else:
            return 0.0
    
    def explain_negation(self, negation: Dict[str, Any]) -> str:
        """
        Generate user-friendly explanation of detected negation
        
        Args:
            negation: Negation dict from detect_negation
        
        Returns:
            User-friendly explanation string
        """
        if not negation.get('present'):
            return ""
        
        scope = negation.get('scope')
        entity = negation.get('entity')
        
        if scope == 'account_type':
            return f"Noted: Excluding {entity} account from this action"
        elif scope == 'amount':
            return f"Noted: Using a minimum amount validation"
        else:
            return "Noted: Special instruction received"


# Helper function for integration with existing extractor
def enhance_extraction_results(
    base_entities: Dict[str, Any],
    message: str,
    intent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhance base entity extraction with Phase 4 features
    
    Args:
        base_entities: Entities from existing extractor
        message: Original user message
        intent: Current intent
    
    Returns:
        Enhanced entities dict with implicit amounts and negation
    """
    enhancer = EnhancedBankingEntityExtractor()
    
    # Get enhanced entities
    enhanced = enhancer.extract_context_aware_entities(message, intent)
    
    # Merge with base entities (enhanced takes precedence)
    merged = {**base_entities, **enhanced}
    
    return merged
