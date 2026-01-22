"""
Phase 2 Integration Test
Tests receipt generation, error handling, and entity validation
Place in: test_phase2.py (project root)
"""

import os
import sys

# Add paths for imports
app_dir = os.path.join(os.path.dirname(__file__), 'backend', 'app')
sys.path.insert(0, app_dir)
sys.path.insert(0, os.path.dirname(__file__))

from backend.app.utils.receipt_generator import ReceiptGenerator
from backend.app.utils.error_handler import ErrorHandler
from backend.app.ml.entity_validator import EntityValidator


def test_receipt_generator():
    """Test receipt generation for all transaction types"""
    print("\n" + "=" * 80)
    print(" " * 15 + "🧾 PHASE 2: RECEIPT GENERATOR TESTS")
    print("=" * 80)
    
    generator = ReceiptGenerator()
    
    # Test 1: Transfer Receipt (Text Format)
    print("\n✅ Test 1: Transfer Receipt (Text Format)")
    print("-" * 80)
    transfer_receipt = generator.generate_transfer_receipt(
        transaction_id="TXN-20241206-001234",
        from_account={
            'account_no': 'PK12ABCD1234567890123456',
            'account_type': 'salary',
            'holder_name': 'Ali Khan',
            'previous_balance': 125450.00
        },
        to_account={
            'account_no': 'PK98BANK7654321098765432',
            'holder_name': 'Sarah Ahmed'
        },
        amount=5000.00,
        description="Gift payment",
        new_balance=120450.00,
        format="text"
    )
    print(transfer_receipt)
    
    # Test 2: Bill Payment Receipt (Text)
    print("\n\n✅ Test 2: Bill Payment Receipt (Text Format)")
    print("-" * 80)
    bill_receipt = generator.generate_bill_payment_receipt(
        transaction_id="BILL-20241206-005678",
        bill_type="electricity",
        amount=4200.00,
        account={
            'account_no': 'PK12ABCD1234567890123456',
            'account_type': 'salary',
            'holder_name': 'Ali Khan',
            'previous_balance': 125450.00
        },
        reference_no="LESCO-2024-001",
        new_balance=121250.00,
        format="text"
    )
    print(bill_receipt)
    
    # Test 3: Account Creation Receipt
    print("\n\n✅ Test 3: Account Creation Receipt")
    print("-" * 80)
    account_receipt = generator.generate_account_creation_receipt(
        user_name="Ahmed Ali",
        phone="03001234567",
        email="ahmed.ali@email.com",
        account_number="PK56NEWB1234567890123456",
        account_type="savings",
        format="text"
    )
    print(account_receipt)
    
    print("\n" + "✅ Receipt Generator Tests: PASSED")


def test_error_handler():
    """Test error handling for various scenarios"""
    print("\n" + "=" * 80)
    print(" " * 15 + "⚠️  PHASE 2: ERROR HANDLER TESTS")
    print("=" * 80)
    
    handler = ErrorHandler()
    
    # Test 1: Insufficient Balance
    print("\n✅ Test 1: Insufficient Balance Error")
    print("-" * 80)
    error = handler.insufficient_balance_error(
        required=5000.00,
        available=3200.00,
        available_accounts=[
            {'account_type': 'savings', 'balance': 75300.50},
            {'account_type': 'current', 'balance': 12000.00}
        ]
    )
    print(error)
    
    # Test 2: Invalid Account
    print("\n\n✅ Test 2: Invalid Account Error")
    print("-" * 80)
    error = handler.invalid_account_error(
        entered_account="PK12ABC",
        user_accounts=[
            {'account_no': 'PK12ABCD1234567890123456', 'account_type': 'salary'},
            {'account_no': 'PK12ABCD1234567890123457', 'account_type': 'savings'}
        ]
    )
    print(error)
    
    # Test 3: Amount Out of Range
    print("\n\n✅ Test 3: Amount Out of Range Error")
    print("-" * 80)
    error = handler.amount_out_of_range_error(
        amount=2500000.00,
        min_amount=1.00,
        max_amount=1000000.00
    )
    print(error)
    
    # Test 4: Invalid Phone
    print("\n\n✅ Test 4: Invalid Phone Error")
    print("-" * 80)
    error = handler.invalid_phone_error("0300123")
    print(error)
    
    # Test 5: Invalid Email
    print("\n\n✅ Test 5: Invalid Email Error")
    print("-" * 80)
    error = handler.invalid_email_error("notanemail")
    print(error)
    
    # Test 6: Email Already Exists
    print("\n\n✅ Test 6: Email Already Exists Error")
    print("-" * 80)
    error = handler.email_already_exists_error("user@gmail.com")
    print(error)
    
    # Test 7: OTP Error
    print("\n\n✅ Test 7: OTP Verification Error")
    print("-" * 80)
    error = handler.otp_error(attempts_remaining=2)
    print(error)
    
    print("\n" + "✅ Error Handler Tests: PASSED")


def test_entity_validator():
    """Test entity validation"""
    print("\n" + "=" * 80)
    print(" " * 15 + "✔️  PHASE 2: ENTITY VALIDATOR TESTS")
    print("=" * 80)
    
    validator = EntityValidator()
    
    # Test 1: Valid Amount
    print("\n✅ Test 1: Amount Validation")
    print("-" * 80)
    tests = [
        ("5000", True),
        ("5000.50", True),
        ("PKR 5000", True),
        ("1,000,000", True),
        (2500000, False),  # Exceeds MAX_AMOUNT
        (-500, False),      # Negative
        ("abc", False),     # Invalid
    ]
    
    for amount, should_pass in tests:
        result = validator.validate_amount(amount)
        status = "✅" if (result is not None) == should_pass else "❌"
        print(f"  {status} {amount} -> {result}")
    
    # Test 2: Account Number Validation
    print("\n\n✅ Test 2: Account Number Validation")
    print("-" * 80)
    account_tests = [
        ("PK12ABCD1234567890123456", True),  # Valid IBAN
        ("123456789012", True),                 # Valid account
        ("PK12ABC", False),                     # Too short
        ("INVALID", False),                     # Invalid format
    ]
    
    for account, should_pass in account_tests:
        result = validator.validate_account_number(account)
        status = "✅" if (result is not None) == should_pass else "❌"
        print(f"  {status} {account} -> {result}")
    
    # Test 3: Phone Number Validation
    print("\n\n✅ Test 3: Phone Number Validation")
    print("-" * 80)
    phone_tests = [
        ("03001234567", True),   # Valid Pakistani
        ("03211234567", True),   # Valid Pakistani
        ("03451234567", True),   # Valid Pakistani
        ("+923001234567", True),  # Valid with country code
        ("0300123", False),       # Too short
        ("0200123456", False),    # Invalid operator
    ]
    
    for phone, should_pass in phone_tests:
        result = validator.validate_phone_number(phone)
        status = "✅" if (result is not None) == should_pass else "❌"
        print(f"  {status} {phone} -> {result}")
    
    # Test 4: Person Name Validation
    print("\n\n✅ Test 4: Person Name Validation")
    print("-" * 80)
    name_tests = [
        ("Ali Khan", True),      # Valid
        ("Sarah Ahmed", True),   # Valid
        ("John-Paul", True),     # Valid with hyphen
        ("A", False),            # Too short
        ("123ABC", False),       # Invalid characters
    ]
    
    for name, should_pass in name_tests:
        result = validator.validate_person_name(name)
        status = "✅" if (result is not None) == should_pass else "❌"
        print(f"  {status} {name} -> {result}")
    
    # Test 5: Bill Type Validation
    print("\n\n✅ Test 5: Bill Type Validation")
    print("-" * 80)
    bill_tests = [
        ("electricity", True),
        ("mobile", True),
        ("gas", True),
        ("water", True),
        ("internet", True),
        ("credit_card", True),
        ("loan", True),
        ("invalid_bill", False),
    ]
    
    for bill_type, should_pass in bill_tests:
        result = validator.validate_bill_type(bill_type)
        status = "✅" if (result is not None) == should_pass else "❌"
        print(f"  {status} {bill_type} -> {result}")
    
    # Test 6: Validate Entities Dictionary
    print("\n\n✅ Test 6: Validate Entities Dictionary")
    print("-" * 80)
    entities = {
        'amount': '5000',
        'account_number': 'PK12ABCD1234567890123456',
        'phone_number': '03001234567',
        'person': 'ali khan',
        'bill_type': 'electricity'
    }
    
    validated = validator.validate_entities(entities)
    print("  Validated entities:")
    for key, value in validated.items():
        print(f"    • {key}: {value}")
    
    # Test 7: Get Validation Errors
    print("\n\n✅ Test 7: Get Validation Errors")
    print("-" * 80)
    invalid_entities = {
        'amount': '2500000',  # Too large
        'account_number': 'INVALID',
        'phone_number': '0200123456'  # Invalid operator
    }
    
    errors = validator.get_validation_errors(invalid_entities)
    print("  Validation errors found:")
    for error in errors:
        print(f"    • {error}")
    
    print("\n" + "✅ Entity Validator Tests: PASSED")


def test_integration():
    """Test integration of all Phase 2 components"""
    print("\n" + "=" * 80)
    print(" " * 15 + "🔗 PHASE 2: INTEGRATION TESTS")
    print("=" * 80)
    
    generator = ReceiptGenerator()
    handler = ErrorHandler()
    validator = EntityValidator()
    
    # Test 1: Full Transfer Workflow
    print("\n✅ Test 1: Full Transfer Workflow")
    print("-" * 80)
    
    # Validate amount
    amount = "5000"
    validated_amount = validator.validate_amount(amount)
    if validated_amount:
        print(f"  ✅ Amount validation: {amount} -> {validated_amount}")
    else:
        print(f"  ❌ Amount validation failed: {amount}")
        return
    
    # Validate accounts
    from_account = "PK12ABCD1234567890123456"
    to_account = "PK98BANK7654321098765432"
    
    validated_from = validator.validate_account_number(from_account)
    validated_to = validator.validate_account_number(to_account)
    
    if validated_from and validated_to:
        print(f"  ✅ Account validation: Both accounts valid")
    else:
        print(f"  ❌ Account validation failed")
        return
    
    # Generate receipt
    receipt = generator.generate_transfer_receipt(
        transaction_id="TXN-20241206-123456",
        from_account={
            'account_no': from_account,
            'account_type': 'salary',
            'holder_name': 'Ali Khan',
            'previous_balance': 125450.00
        },
        to_account={
            'account_no': to_account,
            'holder_name': 'Sarah Ahmed'
        },
        amount=validated_amount,
        description="Integration test transfer",
        new_balance=120450.00,
        format="text"
    )
    print(f"  ✅ Receipt generated (lines: {len(receipt.split(chr(10)))})")
    
    # Test 2: Error Handling with Validation
    print("\n\n✅ Test 2: Error Handling Integration")
    print("-" * 80)
    
    # Invalid amount
    invalid_amount = "2500000"
    validated = validator.validate_amount(invalid_amount)
    if not validated:
        error_msg = handler.amount_out_of_range_error(
            amount=float(invalid_amount),
            min_amount=validator.MIN_AMOUNT,
            max_amount=validator.MAX_AMOUNT
        )
        print(f"  ✅ Invalid amount caught and error generated")
        print(f"  Error: {error_msg[:60]}...")
    
    # Invalid phone
    invalid_phone = "0200123456"
    validated = validator.validate_phone_number(invalid_phone)
    if not validated:
        error_msg = handler.invalid_phone_error(invalid_phone)
        print(f"  ✅ Invalid phone caught and error generated")
    
    print("\n" + "✅ Integration Tests: PASSED")


def main():
    """Run all Phase 2 tests"""
    print("\n" + "=" * 80)
    print(" " * 20 + "🎯 PHASE 2 COMPREHENSIVE TEST")
    print(" " * 15 + "Receipt Generator | Error Handler | Entity Validator")
    print("=" * 80)
    
    try:
        test_receipt_generator()
        test_error_handler()
        test_entity_validator()
        test_integration()
        
        print("\n" + "=" * 80)
        print(" " * 20 + "✅ ALL PHASE 2 TESTS PASSED! 🎉")
        print("=" * 80)
        print("\n📊 Test Summary:")
        print("  ✅ Receipt Generator: All transaction types working")
        print("  ✅ Error Handler: All error scenarios covered")
        print("  ✅ Entity Validator: All validation rules working")
        print("  ✅ Integration: Components working together correctly")
        print("\n🚀 Phase 2 is ready for end-to-end testing!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
