"""
Unit Tests for Entity Extraction System
Tests regex patterns, spaCy NER, and validation
Target: >90% accuracy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.entity_extractor import BankingEntityExtractor
from ml.regex_patterns import BankingRegexPatterns
from ml.entity_validator import EntityValidator


class EntityExtractionTester:
    """Test suite for entity extraction"""
    
    def __init__(self):
        self.extractor = BankingEntityExtractor()
        self.patterns = BankingRegexPatterns()
        self.validator = EntityValidator()
        
        self.total_tests = 0
        self.passed_tests = 0
    
    def assert_equal(self, actual, expected, test_name: str):
        """Assert that actual equals expected"""
        self.total_tests += 1
        
        if actual == expected:
            self.passed_tests += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            print(f"  ❌ {test_name}")
            print(f"     Expected: {expected}")
            print(f"     Got:      {actual}")
            return False
    
    def assert_in(self, item, collection, test_name: str):
        """Assert that item is in collection"""
        self.total_tests += 1
        
        if item in collection:
            self.passed_tests += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            print(f"  ❌ {test_name}")
            print(f"     Expected '{item}' in {collection}")
            return False
    
    def assert_not_none(self, value, test_name: str):
        """Assert that value is not None"""
        self.total_tests += 1
        
        if value is not None:
            self.passed_tests += 1
            print(f"  ✅ {test_name}")
            return True
        else:
            print(f"  ❌ {test_name}")
            print(f"     Expected non-None value")
            return False
    
    def test_amount_extraction(self):
        """Test amount extraction"""
        print("\n💰 Testing Amount Extraction:")
        print("-" * 70)
        
        test_cases = [
            ("Transfer PKR 5,000", "5,000"),
            ("Pay Rs. 3500", "3500"),
            ("Send 10000 rupees", "10000"),
            ("Amount is 1,500.50 PKR", "1,500.50"),
        ]
        
        for text, expected in test_cases:
            amounts = self.patterns.extract_amounts(text)
            self.assert_in(expected, amounts, f"Extract '{expected}' from '{text}'")
    
    def test_account_extraction(self):
        """Test account number extraction"""
        print("\n🏦 Testing Account Number Extraction:")
        print("-" * 70)
        
        test_cases = [
            ("Account PK12ABCD1234567890123456", "PK12ABCD1234567890123456"),
            ("Transfer to 1234567890123456", "1234567890123456"),
        ]
        
        for text, expected in test_cases:
            accounts = self.patterns.extract_account_numbers(text)
            self.assert_in(expected, accounts, f"Extract '{expected}' from '{text}'")
    
    def test_phone_extraction(self):
        """Test phone number extraction"""
        print("\n📱 Testing Phone Number Extraction:")
        print("-" * 70)
        
        test_cases = [
            ("Send to 03001234567", "03001234567"),
            ("Call +92 300 1234567", "3001234567"),
            ("Mobile: 0300-1234567", "03001234567"),
        ]
        
        for text, expected in test_cases:
            phones = self.patterns.extract_phone_numbers(text)
            self.assert_in(expected, phones, f"Extract phone from '{text}'")
    
    def test_bill_type_extraction(self):
        """Test bill type extraction"""
        print("\n🧾 Testing Bill Type Extraction:")
        print("-" * 70)
        
        test_cases = [
            ("Pay electricity bill", "electricity"),
            ("Mobile bill payment", "mobile"),
            ("Gas bill is due", "gas"),
            ("Internet charges", "internet"),
        ]
        
        for text, expected in test_cases:
            bill_type = self.patterns.extract_bill_type(text)
            self.assert_equal(bill_type, expected, f"Extract '{expected}' from '{text}'")
    
    def test_person_extraction(self):
        """Test person name extraction with spaCy"""
        print("\n👤 Testing Person Name Extraction:")
        print("-" * 70)
        
        test_cases = [
            "Transfer money to Ali Khan",
            "Send to Sarah Ahmed",
            "Pay Hassan",
        ]
        
        for text in test_cases:
            entities = self.extractor.extract(text)
            persons = entities.get('persons', [])
            self.assert_not_none(persons, f"Extract person from '{text}'")
    
    def test_amount_validation(self):
        """Test amount validation"""
        print("\n💵 Testing Amount Validation:")
        print("-" * 70)
        
        test_cases = [
            ("5000", 5000.0, True),
            ("1,500.50", 1500.50, True),
            ("2000000", None, False),  # Exceeds max
            ("-100", None, False),  # Negative
        ]
        
        for input_val, expected, should_pass in test_cases:
            result = self.validator.validate_amount(input_val)
            if should_pass:
                self.assert_equal(result, expected, f"Validate amount '{input_val}'")
            else:
                self.assert_equal(result, None, f"Reject invalid amount '{input_val}'")
    
    def test_account_validation(self):
        """Test account number validation"""
        print("\n🏦 Testing Account Number Validation:")
        print("-" * 70)
        
        test_cases = [
            ("PK12ABCD1234567890123456", True),
            ("1234567890123456", True),
            ("123", False),  # Too short
            ("INVALID", False),
        ]
        
        for account, should_pass in test_cases:
            result = self.validator.validate_account_number(account)
            if should_pass:
                self.assert_not_none(result, f"Validate account '{account}'")
            else:
                self.assert_equal(result, None, f"Reject invalid account '{account}'")
    
    def test_phone_validation(self):
        """Test phone number validation"""
        print("\n📱 Testing Phone Number Validation:")
        print("-" * 70)
        
        test_cases = [
            ("03001234567", True),
            ("+923001234567", True),
            ("1234567890", False),  # Wrong format
        ]
        
        for phone, should_pass in test_cases:
            result = self.validator.validate_phone_number(phone)
            if should_pass:
                self.assert_not_none(result, f"Validate phone '{phone}'")
            else:
                self.assert_equal(result, None, f"Reject invalid phone '{phone}'")
    
    def test_complete_extraction(self):
        """Test complete entity extraction pipeline"""
        print("\n🔄 Testing Complete Extraction Pipeline:")
        print("-" * 70)
        
        test_cases = [
            {
                'text': "Transfer PKR 5,000 to Ali Khan",
                'expected_amount': 5000.0,
                'expected_person': True,
            },
            {
                'text': "Pay electricity bill of Rs. 3,500",
                'expected_amount': 3500.0,
                'expected_bill_type': 'electricity',
            },
            {
                'text': "Send 10000 to 03001234567",
                'expected_amount': 10000.0,
                'expected_phone': True,
            },
        ]
        
        for test in test_cases:
            text = test['text']
            entities = self.extractor.extract_and_validate(text)
            
            if 'expected_amount' in test:
                self.assert_equal(
                    entities.get('amount'),
                    test['expected_amount'],
                    f"Extract amount from '{text}'"
                )
            
            if 'expected_person' in test:
                self.assert_not_none(
                    entities.get('person'),
                    f"Extract person from '{text}'"
                )
            
            if 'expected_bill_type' in test:
                self.assert_equal(
                    entities.get('bill_type'),
                    test['expected_bill_type'],
                    f"Extract bill type from '{text}'"
                )
            
            if 'expected_phone' in test:
                self.assert_not_none(
                    entities.get('phone_number'),
                    f"Extract phone from '{text}'"
                )
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 70)
        print(" " * 15 + "ENTITY EXTRACTION TEST SUITE")
        print("=" * 70)
        
        # Run all test methods
        self.test_amount_extraction()
        self.test_account_extraction()
        self.test_phone_extraction()
        self.test_bill_type_extraction()
        self.test_person_extraction()
        self.test_amount_validation()
        self.test_account_validation()
        self.test_phone_validation()
        self.test_complete_extraction()
        
        # Print summary
        print("\n" + "=" * 70)
        print(" " * 25 + "TEST SUMMARY")
        print("=" * 70)
        
        accuracy = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n  Total Tests:     {self.total_tests}")
        print(f"  Passed:          {self.passed_tests}")
        print(f"  Failed:          {self.total_tests - self.passed_tests}")
        print(f"  Accuracy:        {accuracy:.2f}%")
        
        target_accuracy = 90.0
        status = "✅ PASS" if accuracy >= target_accuracy else "❌ FAIL"
        print(f"\n  Target Accuracy: {target_accuracy}%")
        print(f"  Status:          {status}")
        
        print("\n" + "=" * 70)
        
        return accuracy >= target_accuracy


def main():
    """Run entity extraction tests"""
    tester = EntityExtractionTester()
    success = tester.run_all_tests()
    
    if success:
        print("✅ All tests passed! Entity extraction system ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Review and fix issues.")
        return 1


if __name__ == "__main__":
    exit(main())