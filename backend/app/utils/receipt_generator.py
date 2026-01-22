"""
Receipt Generator
Creates professional transaction receipts in text and JSON formats
Place in: backend/app/utils/receipt_generator.py
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json


class ReceiptGenerator:
    """
    Generates transaction receipts for banking operations
    """
    
    def __init__(self):
        """Initialize receipt generator"""
        self.currency = "PKR"
    
    def generate_transfer_receipt(self, 
                                  transaction_id: str,
                                  from_account: Dict[str, Any],
                                  to_account: Dict[str, Any],
                                  amount: float,
                                  description: str = "",
                                  new_balance: Optional[float] = None,
                                  format: str = "text") -> str:
        """
        Generate money transfer receipt
        
        Args:
            transaction_id: Transaction ID
            from_account: Source account details
            to_account: Destination account details
            amount: Transfer amount
            description: Transaction description
            new_balance: Balance after transaction
            format: "text" or "json"
            
        Returns:
            Formatted receipt string
        """
        timestamp = datetime.now()
        
        if format == "json":
            return self._generate_transfer_json(
                transaction_id, from_account, to_account, 
                amount, description, new_balance, timestamp
            )
        else:
            return self._generate_transfer_text(
                transaction_id, from_account, to_account,
                amount, description, new_balance, timestamp
            )
    
    def _generate_transfer_text(self, transaction_id, from_account, to_account,
                                amount, description, new_balance, timestamp) -> str:
        """Generate text format receipt"""
        
        from_masked = self._mask_account(from_account.get('account_no', ''))
        to_masked = self._mask_account(to_account.get('account_no', ''))
        
        receipt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       TRANSACTION RECEIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Transaction ID: {transaction_id}
Date: {timestamp.strftime('%B %d, %Y at %H:%M PKT')}
Type: Money Transfer

FROM
├─ Account: {from_masked} ({from_account.get('account_type', 'N/A').title()})
├─ Name: {from_account.get('holder_name', 'N/A')}
└─ Previous Balance: {self.currency} {from_account.get('previous_balance', 0):,.2f}

TO
├─ Account: {to_masked}
└─ Name: {to_account.get('holder_name', 'N/A')}
"""
        
        if description:
            receipt += f"└─ Reference: {description}\n"
        
        receipt += f"""
TRANSACTION DETAILS
├─ Amount: {self.currency} {amount:,.2f}
├─ Fee: {self.currency} 0.00
├─ Total Deducted: {self.currency} {amount:,.2f}
└─ Status: ✅ SUCCESS
"""
        
        if new_balance is not None:
            receipt += f"""
AFTER TRANSACTION
└─ New Balance: {self.currency} {new_balance:,.2f}
"""
        
        receipt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Need help? Type 'help' or 'support'
Receipt generated at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return receipt.strip()
    
    def _generate_transfer_json(self, transaction_id, from_account, to_account,
                                amount, description, new_balance, timestamp) -> str:
        """Generate JSON format receipt"""
        
        receipt_data = {
            "receipt": {
                "transaction_id": transaction_id,
                "timestamp": timestamp.isoformat(),
                "type": "transfer",
                "status": "success",
                "from": {
                    "account_number": from_account.get('account_no', ''),
                    "masked_number": self._mask_account(from_account.get('account_no', '')),
                    "account_type": from_account.get('account_type', ''),
                    "holder_name": from_account.get('holder_name', ''),
                    "previous_balance": from_account.get('previous_balance', 0)
                },
                "to": {
                    "account_number": to_account.get('account_no', ''),
                    "masked_number": self._mask_account(to_account.get('account_no', '')),
                    "holder_name": to_account.get('holder_name', '')
                },
                "amounts": {
                    "principal": amount,
                    "fee": 0.00,
                    "total": amount,
                    "currency": self.currency,
                    "new_balance": new_balance
                },
                "metadata": {
                    "description": description,
                    "initiated_by": "chatbot",
                    "reference": f"REF-{transaction_id}"
                }
            }
        }
        
        return json.dumps(receipt_data, indent=2)
    
    def generate_bill_payment_receipt(self,
                                      transaction_id: str,
                                      bill_type: str,
                                      amount: float,
                                      account: Dict[str, Any],
                                      reference_no: Optional[str] = None,
                                      new_balance: Optional[float] = None,
                                      format: str = "text") -> str:
        """
        Generate bill payment receipt
        
        Args:
            transaction_id: Transaction ID
            bill_type: Type of bill
            amount: Payment amount
            account: Payment account details
            reference_no: Bill reference number
            new_balance: Balance after payment
            format: "text" or "json"
            
        Returns:
            Formatted receipt string
        """
        timestamp = datetime.now()
        
        if format == "json":
            return self._generate_bill_payment_json(
                transaction_id, bill_type, amount, account,
                reference_no, new_balance, timestamp
            )
        else:
            return self._generate_bill_payment_text(
                transaction_id, bill_type, amount, account,
                reference_no, new_balance, timestamp
            )
    
    def _generate_bill_payment_text(self, transaction_id, bill_type, amount,
                                    account, reference_no, new_balance, timestamp) -> str:
        """Generate text format bill payment receipt"""
        
        account_masked = self._mask_account(account.get('account_no', ''))
        bill_name = self._get_bill_display_name(bill_type)
        
        receipt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      BILL PAYMENT RECEIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Transaction ID: {transaction_id}
Date: {timestamp.strftime('%B %d, %Y at %H:%M PKT')}
Type: Bill Payment

BILL DETAILS
├─ Bill Type: {bill_name}
"""
        
        if reference_no:
            receipt += f"├─ Reference: {reference_no}\n"
        
        receipt += f"""├─ Amount: {self.currency} {amount:,.2f}
└─ Status: ✅ PAID

PAYMENT FROM
├─ Account: {account_masked} ({account.get('account_type', 'N/A').title()})
├─ Name: {account.get('holder_name', 'N/A')}
└─ Previous Balance: {self.currency} {account.get('previous_balance', 0):,.2f}
"""
        
        if new_balance is not None:
            receipt += f"""
AFTER PAYMENT
└─ New Balance: {self.currency} {new_balance:,.2f}
"""
        
        receipt += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Thank you for using our service! 🎉
Receipt generated at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return receipt.strip()
    
    def _generate_bill_payment_json(self, transaction_id, bill_type, amount,
                                    account, reference_no, new_balance, timestamp) -> str:
        """Generate JSON format bill payment receipt"""
        
        receipt_data = {
            "receipt": {
                "transaction_id": transaction_id,
                "timestamp": timestamp.isoformat(),
                "type": "bill_payment",
                "status": "success",
                "bill": {
                    "type": bill_type,
                    "display_name": self._get_bill_display_name(bill_type),
                    "reference_number": reference_no,
                    "amount": amount
                },
                "payment_account": {
                    "account_number": account.get('account_no', ''),
                    "masked_number": self._mask_account(account.get('account_no', '')),
                    "account_type": account.get('account_type', ''),
                    "holder_name": account.get('holder_name', ''),
                    "previous_balance": account.get('previous_balance', 0)
                },
                "amounts": {
                    "principal": amount,
                    "fee": 0.00,
                    "total": amount,
                    "currency": self.currency,
                    "new_balance": new_balance
                }
            }
        }
        
        return json.dumps(receipt_data, indent=2)
    
    def generate_account_creation_receipt(self,
                                          user_name: str,
                                          phone: str,
                                          email: str,
                                          account_number: str,
                                          account_type: str,
                                          format: str = "text") -> str:
        """
        Generate account creation receipt
        
        Args:
            user_name: User's name
            phone: Phone number
            email: Email address
            account_number: New account number
            account_type: Account type
            format: "text" or "json"
            
        Returns:
            Formatted receipt string
        """
        timestamp = datetime.now()
        registration_id = f"REG-{timestamp.strftime('%Y%m%d')}-{account_number[-6:]}"
        
        if format == "json":
            return self._generate_account_creation_json(
                registration_id, user_name, phone, email,
                account_number, account_type, timestamp
            )
        else:
            return self._generate_account_creation_text(
                registration_id, user_name, phone, email,
                account_number, account_type, timestamp
            )
    
    def _generate_account_creation_text(self, registration_id, user_name, phone,
                                        email, account_number, account_type, timestamp) -> str:
        """Generate text format account creation receipt"""
        
        account_masked = self._mask_account(account_number)
        
        receipt = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ACCOUNT OPENING CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Registration ID: {registration_id}
Date: {timestamp.strftime('%B %d, %Y at %H:%M PKT')}

ACCOUNT HOLDER DETAILS
├─ Name: {user_name}
├─ Phone: {phone}
└─ Email: {email} ✅

ACCOUNT DETAILS
├─ Account Number: {account_masked}
├─ Full Number: {account_number}
├─ Type: {account_type.title()} Account
├─ Currency: {self.currency}
├─ Opening Balance: {self.currency} 0.00
└─ Status: ✅ ACTIVE

NEXT STEPS
1. You can now deposit funds
2. Start using banking services
3. Request debit card (optional)

Welcome to the bank! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return receipt.strip()
    
    def _generate_account_creation_json(self, registration_id, user_name, phone,
                                        email, account_number, account_type, timestamp) -> str:
        """Generate JSON format account creation receipt"""
        
        receipt_data = {
            "receipt": {
                "registration_id": registration_id,
                "timestamp": timestamp.isoformat(),
                "type": "account_creation",
                "status": "success",
                "account_holder": {
                    "name": user_name,
                    "phone": phone,
                    "email": email,
                    "email_verified": True
                },
                "account": {
                    "account_number": account_number,
                    "masked_number": self._mask_account(account_number),
                    "account_type": account_type,
                    "currency": self.currency,
                    "opening_balance": 0.00,
                    "status": "active"
                }
            }
        }
        
        return json.dumps(receipt_data, indent=2)
    
    def _mask_account(self, account_number: str) -> str:
        """
        Mask account number for security
        
        Args:
            account_number: Full account number
            
        Returns:
            Masked account number (e.g., PK12****3456)
        """
        if not account_number or len(account_number) < 8:
            return account_number
        
        return account_number[:4] + "****" + account_number[-4:]
    
    def _get_bill_display_name(self, bill_type: str) -> str:
        """Get display name for bill type"""
        bill_names = {
            'electricity': 'Electricity (LESCO)',
            'mobile': 'Mobile Bill',
            'gas': 'Gas (SSGC)',
            'water': 'Water Bill',
            'internet': 'Internet / Broadband',
            'credit_card': 'Credit Card Payment',
            'loan': 'Loan Payment'
        }
        return bill_names.get(bill_type, bill_type.title())
    
    def generate_transaction_id(self, transaction_type: str = "TXN") -> str:
        """
        Generate unique transaction ID
        
        Args:
            transaction_type: Type prefix (TXN, BILL, REG)
            
        Returns:
            Transaction ID (e.g., TXN-20241206-001234)
        """
        timestamp = datetime.now()
        random_suffix = f"{timestamp.microsecond:06d}"
        return f"{transaction_type}-{timestamp.strftime('%Y%m%d')}-{random_suffix}"


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print(" " * 20 + "RECEIPT GENERATOR TEST")
    print("=" * 80)
    
    generator = ReceiptGenerator()
    
    # Test 1: Transfer Receipt (Text)
    print("\n📝 Test 1: Transfer Receipt (Text Format)")
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
    print("\n\n📝 Test 2: Bill Payment Receipt (Text Format)")
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
    print("\n\n📝 Test 3: Account Creation Receipt (Text Format)")
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
    
    # Test 4: JSON Format
    print("\n\n📝 Test 4: Transfer Receipt (JSON Format)")
    print("-" * 80)
    
    transfer_json = generator.generate_transfer_receipt(
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
        format="json"
    )
    
    print(transfer_json)
    
    print("\n" + "=" * 80)
    print("✅ Receipt generator tests complete!")