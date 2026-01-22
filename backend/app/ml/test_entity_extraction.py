"""
Entity Extraction Test Suite
Comprehensive tests for banking entity extraction system
"""

from app.ml.regex_patterns import BankingRegexPatterns
from app.ml.entity_extractor import BankingEntityExtractor
from app.ml.entity_validator import EntityValidator
from typing import Dict, List, Any


class EntityExtractionTester:
    """Test suite for entity extraction system"""
    
    def __init__(self):
        """Initialize tester with extractors"""
        self.extractor = BankingEntityExtractor()
        self.validator = EntityValidator()
        self.test_cases = self._get_test_cases()
        self.passed = 0
        self.failed = 0
        
    def _get_test_cases(self) -> List[Dict[str, Any]]:
        """Get comprehensive test cases"""
        return [
            # Amount tests
            {
                "query": "Transfer PKR 5,000 to account",
                "expected_amount": 5000,
                "description": "Amount with PKR currency"
            },
            {
                "query": "Pay Rs. 3,500 for bill",
                "expected_amount": 3500,
                "description": "Amount with Rs. currency"
            },
            {
                "query": "Send 10000 rupees to contact",
                "expected_amount": 10000,
                "description": "Amount with rupees word"
            },
            {
                "query": "Withdraw 20000 from account",
                "expected_amount": 20000,
                "description": "Large amount without currency"
            },
            {
                "query": "Pay 1,500.50 for utilities",
                "expected_amount": 1500.50,
                "description": "Amount with decimals"
            },
            
            # Account number tests
            {
                "query": "Transfer to account PK12ABCD1234567890123456",
                "expected_account": "PK12ABCD1234567890123456",
                "description": "IBAN format account"
            },
            {
                "query": "My account 1234567890123456 needs check",
                "expected_account": "1234567890123456",
                "description": "16-digit account number"
            },
            {
                "query": "Account number 123456789012 is blocked",
                "expected_account": "123456789012",
                "description": "12-digit account number"
            },
            
            # Phone number tests
            {
                "query": "Send money to 03001234567",
                "expected_phone": "03001234567",
                "description": "11-digit Pakistani phone"
            },
            {
                "query": "Call 92 300 1234567 for support",
                "expected_phone": "92 300 1234567",
                "description": "Phone with country code"
            },
            {
                "query": "My number is 0321-9876543",
                "expected_phone": "0321-9876543",
                "description": "Phone with hyphen"
            },
            
            # Date tests
            {
                "query": "Due date is 15/12/2024",
                "expected_date": "15/12/2024",
                "description": "DD/MM/YYYY format"
            },
            {
                "query": "Payment due on 2024-12-15",
                "expected_date": "2024-12-15",
                "description": "YYYY-MM-DD format"
            },
            {
                "query": "Deadline 15-Dec-2024",
                "expected_date": "15-Dec-2024",
                "description": "DD-MMM-YYYY format"
            },
            
            # Person name tests
            {
                "query": "Transfer to Ali Khan's account",
                "expected_name": "Ali Khan",
                "description": "Two-word name"
            },
            {
                "query": "Pay Sarah Ahmed 5000 rupees",
                "expected_name": "Sarah Ahmed",
                "description": "Name with amount"
            },
            
            # Complex queries
            {
                "query": "Transfer PKR 5,000 to Ali Khan account PK12ABCD1234567890123456 due 15/12/2024",
                "expected_amount": 5000,
                "expected_name": "Ali Khan",
                "expected_account": "PK12ABCD1234567890123456",
                "expected_date": "15/12/2024",
                "description": "Complex query with multiple entities"
            },
            {
                "query": "Send 10,000 rupees to 03001234567 for mobile bill",
                "expected_amount": 10000,
                "expected_phone": "03001234567",
                "description": "Amount and phone number"
            },
            {
                "query": "Pay electricity bill of Rs. 4,200 account 1234567890123456",
                "expected_amount": 4200,
                "expected_account": "1234567890123456",
                "description": "Amount and account number"
            },
        ]
    
    def test_amount_extraction(self) -> bool:
        """Test amount extraction"""
        print("\n🔍 Test 1: Amount Extraction")
        print("-" * 50)
        
        passed = 0
        total = 0
        
        test_cases = [tc for tc in self.test_cases if 'expected_amount' in tc]
        
        for test in test_cases:
            total += 1
            entities = self.extractor.extract_and_validate(test['query'])
            amount = entities.get('amount')
            
            if amount is not None and abs(amount - test['expected_amount']) < 0.01:
                print(f"   ✅ {test['description']}: {amount}")
                passed += 1
            else:
                print(f"   ❌ {test['description']}: Expected {test['expected_amount']}, got {amount}")
                self.failed += 1
        
        self.passed += passed
        print(f"   Result: {passed}/{total} passed")
        return passed == total
    
    def test_account_extraction(self) -> bool:
        """Test account number extraction"""
        print("\n🔍 Test 2: Account Number Extraction")
        print("-" * 50)
        
        passed = 0
        total = 0
        
        test_cases = [tc for tc in self.test_cases if 'expected_account' in tc]
        
        for test in test_cases:
            total += 1
            entities = self.extractor.extract_and_validate(test['query'])
            account = entities.get('account_number')
            
            if account and account in test['query']:
                print(f"   ✅ {test['description']}: {account}")
                passed += 1
            else:
                print(f"   ❌ {test['description']}: Expected {test['expected_account']}, got {account}")
                self.failed += 1
        
        self.passed += passed
        print(f"   Result: {passed}/{total} passed")
        return passed == total
    
    def test_phone_extraction(self) -> bool:
        """Test phone number extraction"""
        print("\n🔍 Test 3: Phone Number Extraction")
        print("-" * 50)
        
        passed = 0
        total = 0
        
        test_cases = [tc for tc in self.test_cases if 'expected_phone' in tc]
        
        for test in test_cases:
            total += 1
            entities = self.extractor.extract_and_validate(test['query'])
            phone = entities.get('phone_number')
            
            if phone:
                print(f"   ✅ {test['description']}: {phone}")
                passed += 1
            else:
                print(f"   ❌ {test['description']}: No phone found")
                self.failed += 1
        
        self.passed += passed
        print(f"   Result: {passed}/{total} passed")
        return passed == total
    
    def test_date_extraction(self) -> bool:
        """Test date extraction"""
        print("\n🔍 Test 4: Date Extraction")
        print("-" * 50)
        
        passed = 0
        total = 0
        
        test_cases = [tc for tc in self.test_cases if 'expected_date' in tc]
        
        for test in test_cases:
            total += 1
            entities = self.extractor.extract_and_validate(test['query'])
            date = entities.get('date')
            
            if date:
                print(f"   ✅ {test['description']}: {date}")
                passed += 1
            else:
                print(f"   ❌ {test['description']}: No date found")
                self.failed += 1
        
        self.passed += passed
        print(f"   Result: {passed}/{total} passed")
        return passed == total
    
    def test_complex_queries(self) -> bool:
        """Test complex queries with multiple entities"""
        print("\n🔍 Test 5: Complex Query Extraction")
        print("-" * 50)
        
        passed = 0
        total = 0
        
        test_cases = [tc for tc in self.test_cases if 'expected_amount' in tc and 
                      ('expected_name' in tc or 'expected_account' in tc or 'expected_phone' in tc)]
        
        for test in test_cases:
            total += 1
            entities = self.extractor.extract_and_validate(test['query'])
            
            checks = []
            if 'expected_amount' in test:
                amount = entities.get('amount')
                checks.append(amount is not None)
            
            if 'expected_account' in test:
                account = entities.get('account_number')
                checks.append(account is not None)
            
            if 'expected_phone' in test:
                phone = entities.get('phone_number')
                checks.append(phone is not None)
            
            if all(checks):
                print(f"   ✅ {test['description']}")
                passed += 1
            else:
                print(f"   ❌ {test['description']}: Missing entities")
                self.failed += 1
        
        self.passed += passed
        print(f"   Result: {passed}/{total} passed")
        return passed == total
    
    def test_validation(self) -> bool:
        """Test entity validation"""
        print("\n🔍 Test 6: Entity Validation")
        print("-" * 50)
        
        passed = 0
        total = 3
        
        # Test valid amount
        if self.validator.validate_amount(5000):
            print(f"   ✅ Valid amount: 5000")
            passed += 1
        else:
            print(f"   ❌ Valid amount rejected: 5000")
            self.failed += 1
        
        # Test invalid amount (too high)
        if not self.validator.validate_amount(5000000):
            print(f"   ✅ Invalid amount rejected: 5000000")
            passed += 1
        else:
            print(f"   ❌ Invalid amount accepted: 5000000")
            self.failed += 1
        
        # Test invalid amount (negative)
        if not self.validator.validate_amount(-1000):
            print(f"   ✅ Negative amount rejected: -1000")
            passed += 1
        else:
            print(f"   ❌ Negative amount accepted: -1000")
            self.failed += 1
        
        self.passed += passed
        print(f"   Result: {passed}/{total} passed")
        return passed == total
    
    def run_all_tests(self) -> bool:
        """Run all tests and report results"""
        print("\n" + "=" * 80)
        print(" " * 25 + "ENTITY EXTRACTION TEST SUITE")
        print("=" * 80)
        
        results = []
        results.append(self.test_amount_extraction())
        results.append(self.test_account_extraction())
        results.append(self.test_phone_extraction())
        results.append(self.test_date_extraction())
        results.append(self.test_complex_queries())
        results.append(self.test_validation())
        
        # Summary
        print("\n" + "=" * 80)
        print(" " * 30 + "TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_cases) + 3  # +3 for validation tests
        accuracy = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Results:")
        print(f"   Total Tests:  {total_tests}")
        print(f"   Passed:       {self.passed}")
        print(f"   Failed:       {self.failed}")
        print(f"   Accuracy:     {accuracy:.1f}%")
        
        target = 90
        if accuracy >= target:
            print(f"\n✅ Target achieved! ({accuracy:.1f}% >= {target}%)")
            return True
        else:
            print(f"\n⚠️  Target not met ({accuracy:.1f}% < {target}%)")
            return False


if __name__ == "__main__":
    tester = EntityExtractionTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
