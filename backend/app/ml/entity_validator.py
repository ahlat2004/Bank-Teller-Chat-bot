"""
Entity Validation Module
Validates extracted entities according to banking rules
"""

import re
from typing import Optional, Any


class EntityValidator:
    """
    Validates banking entities according to business rules
    """
    
    def __init__(self):
        """Initialize validator with business rules"""
        
        # Validation limits
        self.MIN_AMOUNT = 1.0
        self.MAX_AMOUNT = 1_000_000.0  # 1 million PKR
        
        # Valid bill types
        self.VALID_BILL_TYPES = [
            'electricity', 'mobile', 'gas', 'water', 
            'internet', 'credit_card', 'loan'
        ]
        
        # Account number patterns
        self.IBAN_PATTERN = re.compile(r'^PK\d{2}[A-Z]{4}\d{16}$')
        self.ACCOUNT_PATTERN = re.compile(r'^\d{12,16}$')
        
        # Phone number pattern (Pakistani format)
        self.PHONE_PATTERN = re.compile(r'^03\d{9}$')
    
    def validate_amount(self, amount: Any) -> Optional[float]:
        """
        Validate monetary amount
        
        Args:
            amount: Amount to validate (can be string or float)
            
        Returns:
            Validated amount as float, or None if invalid
        """
        try:
            # Convert to float if string
            if isinstance(amount, str):
                # Remove commas and currency symbols
                amount = amount.replace(',', '').replace('PKR', '').replace('Rs', '').strip()
                amount = float(amount)
            
            amount = float(amount)
            
            # Check range
            if self.MIN_AMOUNT <= amount <= self.MAX_AMOUNT:
                return round(amount, 2)  # Round to 2 decimal places
            else:
                print(f"⚠️  Amount {amount} out of valid range ({self.MIN_AMOUNT}-{self.MAX_AMOUNT})")
                return None
                
        except (ValueError, TypeError):
            print(f"⚠️  Invalid amount format: {amount}")
            return None
    
    def validate_account_number(self, account: str) -> Optional[str]:
        """
        Validate account number format
        
        Args:
            account: Account number to validate
            
        Returns:
            Validated account number, or None if invalid
        """
        if not account:
            return None
        
        account = account.strip().upper()
        
        # Check IBAN format
        if self.IBAN_PATTERN.match(account):
            return account
        
        # Check standard account number
        if self.ACCOUNT_PATTERN.match(account):
            return account
        
        print(f"⚠️  Invalid account number format: {account}")
        return None
    
    def validate_phone_number(self, phone: str) -> Optional[str]:
        """
        Validate phone number (Pakistani format)
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Validated phone number, or None if invalid
        """
        if not phone:
            return None
        
        # Remove spaces and dashes
        phone = phone.replace(' ', '').replace('-', '')
        
        # Check format
        if self.PHONE_PATTERN.match(phone):
            return phone
        
        # Try to fix common issues
        if phone.startswith('+92'):
            phone = '0' + phone[3:]
            if self.PHONE_PATTERN.match(phone):
                return phone
        
        print(f"⚠️  Invalid phone number format: {phone}")
        return None
    
    def validate_person_name(self, name: str) -> Optional[str]:
        """
        Validate and normalize person name
        
        Args:
            name: Person name to validate
            
        Returns:
            Normalized name in title case, or None if invalid
        """
        if not name:
            return None
        
        name = name.strip()
        
        # Check minimum length
        if len(name) < 2:
            print(f"⚠️  Name too short: {name}")
            return None
        
        # Check for valid characters (letters, spaces, hyphens)
        if not re.match(r'^[A-Za-z\s\-\.]+$', name):
            print(f"⚠️  Invalid characters in name: {name}")
            return None
        
        # Normalize to title case
        return name.title()
    
    def validate_bill_type(self, bill_type: str) -> Optional[str]:
        """
        Validate bill type
        
        Args:
            bill_type: Bill type to validate
            
        Returns:
            Validated bill type, or None if invalid
        """
        if not bill_type:
            return None
        
        bill_type = bill_type.lower().strip()
        
        if bill_type in self.VALID_BILL_TYPES:
            return bill_type
        
        print(f"⚠️  Invalid bill type: {bill_type}")
        return None
    
    def validate_date(self, date_str: str) -> Optional[str]:
        """
        Validate date format
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Validated date string, or None if invalid
        """
        if not date_str:
            return None
        
        # For now, just return the string if it exists
        # In production, you'd want to parse and validate the date properly
        # using datetime library
        return date_str.strip()
    
    def validate_entities(self, entities: dict) -> dict:
        """
        Validate all entities in a dictionary
        
        Args:
            entities: Dictionary of entities to validate
            
        Returns:
            Dictionary of validated entities
        """
        validated = {}
        
        # Validate each entity type
        if 'amount' in entities and entities['amount']:
            validated['amount'] = self.validate_amount(entities['amount'])
        
        if 'account_number' in entities and entities['account_number']:
            validated['account_number'] = self.validate_account_number(entities['account_number'])
        
        if 'phone_number' in entities and entities['phone_number']:
            validated['phone_number'] = self.validate_phone_number(entities['phone_number'])
        
        if 'person' in entities and entities['person']:
            validated['person'] = self.validate_person_name(entities['person'])
        
        if 'payee' in entities and entities['payee']:
            validated['payee'] = self.validate_person_name(entities['payee'])
        
        if 'bill_type' in entities and entities['bill_type']:
            validated['bill_type'] = self.validate_bill_type(entities['bill_type'])
        
        if 'date' in entities and entities['date']:
            validated['date'] = self.validate_date(entities['date'])
        
        # Copy non-validated fields
        for key in ['account_type', 'transaction_type']:
            if key in entities:
                validated[key] = entities[key]
        
        return validated
    
    def get_validation_errors(self, entities: dict) -> list:
        """
        Get list of validation errors
        
        Args:
            entities: Dictionary of entities to check
            
        Returns:
            List of error messages
        """
        errors = []
        
        if 'amount' in entities:
            if not self.validate_amount(entities['amount']):
                errors.append(f"Invalid amount: {entities['amount']}")
        
        if 'account_number' in entities:
            if not self.validate_account_number(entities['account_number']):
                errors.append(f"Invalid account number: {entities['account_number']}")
        
        if 'phone_number' in entities:
            if not self.validate_phone_number(entities['phone_number']):
                errors.append(f"Invalid phone number: {entities['phone_number']}")
        
        return errors


# Test the validator
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "ENTITY VALIDATION TEST")
    print("=" * 70)
    
    validator = EntityValidator()
    
    # Test amounts
    print("\n💰 Testing Amount Validation:")
    print("-" * 70)
    test_amounts = ["5000", "1,500.50", "PKR 10000", "2000000", "-100", "abc"]
    
    for amount in test_amounts:
        result = validator.validate_amount(amount)
        status = "✅" if result else "❌"
        print(f"  {status} {amount:15s} → {result}")
    
    # Test account numbers
    print("\n🏦 Testing Account Number Validation:")
    print("-" * 70)
    test_accounts = [
        "PK12ABCD1234567890123456",
        "1234567890123456",
        "123",  # Too short
        "INVALID"
    ]
    
    for account in test_accounts:
        result = validator.validate_account_number(account)
        status = "✅" if result else "❌"
        print(f"  {status} {account:30s} → {result}")
    
    # Test phone numbers
    print("\n📱 Testing Phone Number Validation:")
    print("-" * 70)
    test_phones = [
        "03001234567",
        "+923001234567",
        "0300-1234567",
        "1234567890",  # Invalid
        "03XX1234567"  # Invalid
    ]
    
    for phone in test_phones:
        result = validator.validate_phone_number(phone)
        status = "✅" if result else "❌"
        print(f"  {status} {phone:20s} → {result}")
    
    # Test person names
    print("\n👤 Testing Person Name Validation:")
    print("-" * 70)
    test_names = [
        "ali khan",
        "Sarah Ahmed",
        "A",  # Too short
        "John123",  # Invalid characters
        "Dr. Hassan"
    ]
    
    for name in test_names:
        result = validator.validate_person_name(name)
        status = "✅" if result else "❌"
        print(f"  {status} {name:20s} → {result}")
    
    # Test bill types
    print("\n🧾 Testing Bill Type Validation:")
    print("-" * 70)
    test_bills = ["electricity", "mobile", "gas", "invalid_type", "water"]
    
    for bill in test_bills:
        result = validator.validate_bill_type(bill)
        status = "✅" if result else "❌"
        print(f"  {status} {bill:20s} → {result}")
    
    print("\n" + "=" * 70)
    print("✅ Entity validation tests complete!")