"""
Regex Patterns for Banking Entity Extraction
Defines patterns for amounts, account numbers, phone numbers, etc.
"""

import re
from typing import Dict, List, Optional


class BankingRegexPatterns:
    """Collection of regex patterns for banking entities"""
    
    def __init__(self):
        """Initialize all regex patterns"""
        
        # Amount patterns (PKR, Rs, USD, etc.)
        self.AMOUNT_PATTERNS = [
            # PKR 1,000 or PKR 1000 or PKR 1000.50
            r'(?:pkr|rs\.?|₨)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # 1,000 PKR or 1000 PKR
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:pkr|rs\.?|₨|rupees)',
            # Just numbers with commas (likely amounts in context)
            r'\b(\d{1,3}(?:,\d{3})+(?:\.\d{2})?)\b',
            # Simple numbers that could be amounts (1000, 5000, etc.)
            r'\b(\d{4,}(?:\.\d{2})?)\b',
        ]
        
        # Account number patterns
        self.ACCOUNT_PATTERNS = [
            # IBAN format: PK12ABCD1234567890123456 (24 chars)
            r'\b(PK\d{2}[A-Z]{4}\d{16})\b',
            # Standard Pakistani account (12-16 digits)
            r'\b(\d{12,16})\b',
        ]
        
        # Phone number patterns (Pakistani format)
        self.PHONE_PATTERNS = [
            # 03001234567 (11 digits starting with 03)
            r'\b(03\d{9})\b',
            # +92 300 1234567 or +92-300-1234567
            r'\+92[-\s]?(\d{3})[-\s]?(\d{7})',
            # 0300-1234567 or 0300 1234567
            r'\b(03\d{2})[-\s]?(\d{7})\b',
        ]
        
        # Date patterns
        self.DATE_PATTERNS = [
            # DD/MM/YYYY or DD-MM-YYYY
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b',
            # Month names: 15 January 2024
            r'\b(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})\b',
        ]
        
        # Bill types
        self.BILL_TYPES = [
            'electricity', 'electric', 'bijli',
            'mobile', 'phone', 'cell',
            'gas', 'sui gas',
            'water', 'pani',
            'internet', 'broadband', 'wifi',
            'credit card', 'card',
            'loan', 'installment'
        ]
        
        # Compile all patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        self.amount_regex = [re.compile(p, re.IGNORECASE) for p in self.AMOUNT_PATTERNS]
        self.account_regex = [re.compile(p) for p in self.ACCOUNT_PATTERNS]
        self.phone_regex = [re.compile(p) for p in self.PHONE_PATTERNS]
        self.date_regex = [re.compile(p, re.IGNORECASE) for p in self.DATE_PATTERNS]
    
    def extract_amounts(self, text: str) -> List[str]:
        """
        Extract monetary amounts from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted amounts
        """
        amounts = []
        
        for pattern in self.amount_regex:
            matches = pattern.findall(text)
            if matches:
                # Handle tuples from groups
                for match in matches:
                    if isinstance(match, tuple):
                        amounts.extend([m for m in match if m])
                    else:
                        amounts.append(match)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_amounts = []
        for amount in amounts:
            if amount not in seen:
                seen.add(amount)
                unique_amounts.append(amount)
        
        return unique_amounts
    
    def extract_account_numbers(self, text: str) -> List[str]:
        """
        Extract account numbers from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted account numbers
        """
        accounts = []
        
        for pattern in self.account_regex:
            matches = pattern.findall(text)
            accounts.extend(matches)
        
        return list(set(accounts))  # Remove duplicates
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        Extract phone numbers from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted phone numbers
        """
        phones = []
        
        for pattern in self.phone_regex:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    # Combine parts: (03, 001234567) -> 03001234567
                    phone = ''.join(match)
                    phones.append(phone)
                else:
                    phones.append(match)
        
        return list(set(phones))  # Remove duplicates
    
    def extract_dates(self, text: str) -> List[str]:
        """
        Extract dates from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted dates
        """
        dates = []
        
        for pattern in self.date_regex:
            matches = pattern.findall(text)
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates
    
    def extract_bill_type(self, text: str) -> Optional[str]:
        """
        Extract bill type from text
        
        Args:
            text: Input text
            
        Returns:
            Bill type if found, None otherwise
        """
        text_lower = text.lower()
        
        for bill_type in self.BILL_TYPES:
            if bill_type in text_lower:
                # Return standardized name
                if bill_type in ['electricity', 'electric', 'bijli']:
                    return 'electricity'
                elif bill_type in ['mobile', 'phone', 'cell']:
                    return 'mobile'
                elif bill_type in ['gas', 'sui gas']:
                    return 'gas'
                elif bill_type in ['water', 'pani']:
                    return 'water'
                elif bill_type in ['internet', 'broadband', 'wifi']:
                    return 'internet'
                elif bill_type in ['credit card', 'card']:
                    return 'credit_card'
                elif bill_type in ['loan', 'installment']:
                    return 'loan'
        
        return None
    
    def extract_all(self, text: str) -> Dict[str, List]:
        """
        Extract all entities from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with all extracted entities
        """
        return {
            'amounts': self.extract_amounts(text),
            'account_numbers': self.extract_account_numbers(text),
            'phone_numbers': self.extract_phone_numbers(text),
            'dates': self.extract_dates(text),
            'bill_type': self.extract_bill_type(text)
        }


# Test the patterns
if __name__ == "__main__":
    patterns = BankingRegexPatterns()
    
    # Test cases
    test_texts = [
        "Transfer PKR 5,000 to account PK12ABCD1234567890123456",
        "Pay my electricity bill of Rs. 3500",
        "Send 10000 to 03001234567",
        "Check balance for account 1234567890123456",
        "My mobile bill is 1,500 rupees due on 15/12/2024"
    ]
    
    print("Testing Regex Patterns:\n" + "=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        print("-" * 60)
        entities = patterns.extract_all(text)
        
        for entity_type, values in entities.items():
            if values:
                print(f"  {entity_type}: {values}")
    
    print("\n" + "=" * 60)
    print("✅ Regex pattern tests complete!")