"""
Entity Extraction Module
Combines regex patterns with spaCy NER for comprehensive entity extraction
"""

import spacy
from typing import Dict, List, Optional, Any
import re

from app.ml.regex_patterns import BankingRegexPatterns


class BankingEntityExtractor:
    """
    Banking entity extractor using regex + spaCy NER
    """
    
    def __init__(self, spacy_model: str = 'en_core_web_sm'):
        """
        Initialize entity extractor
        
        Args:
            spacy_model: spaCy model name to load
        """
        print(f"[*] Loading spaCy model: {spacy_model}...")
        
        try:
            self.nlp = spacy.load(spacy_model)
            print("[OK] spaCy model loaded successfully!")
        except OSError:
            print("[*] spaCy model not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", spacy_model])
            self.nlp = spacy.load(spacy_model)
            print("[OK] spaCy model downloaded and loaded!")
        
        # Initialize regex patterns
        self.regex_patterns = BankingRegexPatterns()
        
        # Add custom entity ruler for banking terms
        self._add_custom_patterns()
    
    def _add_custom_patterns(self):
        """Add custom entity patterns to spaCy pipeline"""
        # Create entity ruler if not exists
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        else:
            ruler = self.nlp.get_pipe("entity_ruler")
        
        # Define custom patterns for banking terms
        patterns = [
            {"label": "ACCOUNT_TYPE", "pattern": "savings account"},
            {"label": "ACCOUNT_TYPE", "pattern": "current account"},
            {"label": "ACCOUNT_TYPE", "pattern": "salary account"},
            {"label": "ACCOUNT_TYPE", "pattern": "checking account"},
            {"label": "TRANSACTION_TYPE", "pattern": "transfer"},
            {"label": "TRANSACTION_TYPE", "pattern": "withdrawal"},
            {"label": "TRANSACTION_TYPE", "pattern": "deposit"},
            {"label": "TRANSACTION_TYPE", "pattern": "payment"},
        ]
        
        ruler.add_patterns(patterns)
    
    def extract_with_spacy(self, text: str) -> Dict[str, List[Any]]:
        """
        Extract entities using spaCy NER
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entities found by spaCy
        """
        doc = self.nlp(text)
        
        entities = {
            'persons': [],
            'organizations': [],
            'money': [],
            'dates': [],
            'account_types': [],
            'transaction_types': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                entities['persons'].append(ent.text)
            elif ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entities['money'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'ACCOUNT_TYPE':
                entities['account_types'].append(ent.text)
            elif ent.label_ == 'TRANSACTION_TYPE':
                entities['transaction_types'].append(ent.text)
        
        return entities
    
    def extract_with_regex(self, text: str) -> Dict[str, Any]:
        """
        Extract entities using regex patterns
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entities found by regex
        """
        return self.regex_patterns.extract_all(text)
    
    def merge_entities(self, spacy_entities: Dict, regex_entities: Dict) -> Dict[str, Any]:
        """
        Merge entities from spaCy and regex, prioritizing regex for structured data
        
        Args:
            spacy_entities: Entities extracted by spaCy
            regex_entities: Entities extracted by regex
            
        Returns:
            Merged entity dictionary
        """
        merged = {
            'amount': None,
            'amounts': regex_entities.get('amounts', []),
            'account_number': None,
            'account_numbers': regex_entities.get('account_numbers', []),
            'phone_number': None,
            'phone_numbers': regex_entities.get('phone_numbers', []),
            'person': None,
            'persons': spacy_entities.get('persons', []),
            'payee': None,  # Will be resolved from persons/organizations
            'bill_type': regex_entities.get('bill_type'),
            'date': None,
            'dates': regex_entities.get('dates', []) or spacy_entities.get('dates', []),
            'account_type': spacy_entities.get('account_types', [None])[0] if spacy_entities.get('account_types') else None,
            'transaction_type': spacy_entities.get('transaction_types', [None])[0] if spacy_entities.get('transaction_types') else None
        }
        
        # Set primary values (first occurrence)
        if merged['amounts']:
            merged['amount'] = self._normalize_amount(merged['amounts'][0])
        
        if merged['account_numbers']:
            merged['account_number'] = merged['account_numbers'][0]
        
        if merged['phone_numbers']:
            merged['phone_number'] = merged['phone_numbers'][0]
        
        if merged['dates']:
            merged['date'] = merged['dates'][0]
        
        # Resolve payee (person or organization)
        if merged['persons']:
            merged['person'] = merged['persons'][0]
            merged['payee'] = merged['persons'][0]
        elif spacy_entities.get('organizations'):
            merged['payee'] = spacy_entities['organizations'][0]
        
        return merged
    
    def _normalize_amount(self, amount_str: str) -> float:
        """
        Normalize amount string to float
        
        Args:
            amount_str: Amount as string (e.g., "1,000", "1000.50")
            
        Returns:
            Amount as float
        """
        # Remove commas and convert to float
        normalized = amount_str.replace(',', '')
        
        try:
            return float(normalized)
        except ValueError:
            return 0.0
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        Main extraction method - combines regex and spaCy
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of all extracted entities
        """
        # Extract with both methods
        spacy_entities = self.extract_with_spacy(text)
        regex_entities = self.extract_with_regex(text)
        
        # Merge results
        merged_entities = self.merge_entities(spacy_entities, regex_entities)
        
        return merged_entities
    
    def extract_and_validate(self, text: str) -> Dict[str, Any]:
        """
        Extract entities and validate them
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of validated entities
        """
        entities = self.extract(text)
        
        # Import validator
        from app.ml.entity_validator import EntityValidator
        validator = EntityValidator()
        
        # Validate each entity
        validated = {}
        
        if entities.get('amount'):
            validated['amount'] = validator.validate_amount(entities['amount'])
        
        if entities.get('account_number'):
            validated['account_number'] = validator.validate_account_number(entities['account_number'])
        
        if entities.get('phone_number'):
            validated['phone_number'] = validator.validate_phone_number(entities['phone_number'])
        
        if entities.get('person'):
            validated['person'] = validator.validate_person_name(entities['person'])
        
        if entities.get('bill_type'):
            validated['bill_type'] = validator.validate_bill_type(entities['bill_type'])
        
        # Copy other fields
        validated['payee'] = entities.get('payee')
        validated['date'] = entities.get('date')
        validated['account_type'] = entities.get('account_type')
        validated['transaction_type'] = entities.get('transaction_type')
        
        # Keep all found entities for reference
        validated['all_amounts'] = entities.get('amounts', [])
        validated['all_accounts'] = entities.get('account_numbers', [])
        validated['all_persons'] = entities.get('persons', [])
        
        return validated


# Test the extractor
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "ENTITY EXTRACTION TEST")
    print("=" * 70)
    
    # Initialize extractor
    extractor = BankingEntityExtractor()
    
    # Test cases
    test_cases = [
        "Transfer PKR 5,000 to Ali Khan's account",
        "Pay my electricity bill of Rs. 3,500",
        "Send 10000 to 03001234567",
        "Check balance for account PK12ABCD1234567890123456",
        "Transfer 25,000 rupees to Sarah",
        "My mobile bill is 1,500 due on 15/12/2024",
        "Withdraw 20000 from my savings account"
    ]
    
    print("\n🔍 Testing Entity Extraction:\n")
    
    for i, text in enumerate(test_cases, 1):
        print(f"Test {i}: {text}")
        print("-" * 70)
        
        entities = extractor.extract(text)
        
        # Display extracted entities
        print("📊 Extracted Entities:")
        for key, value in entities.items():
            if value and value != [] and value != [None]:
                print(f"  {key:20s}: {value}")
        
        print()
    
    print("=" * 70)
    print("✅ Entity extraction tests complete!")