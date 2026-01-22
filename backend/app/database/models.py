"""
Database Models
Pydantic models for type safety and validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# Enums
class AccountType(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    SALARY = "salary"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class BillType(str, Enum):
    ELECTRICITY = "electricity"
    MOBILE = "mobile"
    GAS = "gas"
    WATER = "water"
    INTERNET = "internet"
    CREDIT_CARD = "credit_card"
    LOAN = "loan"


class BillStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    OVERDUE = "overdue"


class CardType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    PREPAID = "prepaid"


class CardStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    EXPIRED = "expired"


# Models
class User(BaseModel):
    """User model"""
    id: Optional[int] = None
    name: str
    phone: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Account(BaseModel):
    """Account model"""
    id: Optional[int] = None
    user_id: int
    account_no: str
    account_type: AccountType
    balance: float = Field(ge=0, description="Balance must be non-negative")
    currency: str = "PKR"
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('account_no')
    def validate_account_no(cls, v):
        if len(v) < 12:
            raise ValueError('Account number must be at least 12 characters')
        return v
    
    class Config:
        from_attributes = True


class Transaction(BaseModel):
    """Transaction model"""
    id: Optional[int] = None
    account_id: int
    type: TransactionType
    amount: float = Field(gt=0, description="Amount must be positive")
    payee: Optional[str] = None
    description: Optional[str] = None
    balance_after: Optional[float] = None
    timestamp: Optional[datetime] = None
    meta: Optional[str] = None
    
    class Config:
        from_attributes = True


class Bill(BaseModel):
    """Bill model"""
    id: Optional[int] = None
    user_id: int
    type: BillType
    amount: float = Field(gt=0, description="Amount must be positive")
    due_date: date
    status: BillStatus = BillStatus.UNPAID
    reference_no: Optional[str] = None
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Card(BaseModel):
    """Card model"""
    id: Optional[int] = None
    account_id: int
    card_number: str
    card_type: CardType
    card_name: str
    expiry_date: date
    cvv: str
    status: CardStatus = CardStatus.ACTIVE
    credit_limit: float = 0.0
    created_at: Optional[datetime] = None
    
    @validator('card_number')
    def validate_card_number(cls, v):
        # Remove spaces and validate length
        card_no = v.replace(' ', '')
        if not card_no.isdigit() or len(card_no) not in [15, 16]:
            raise ValueError('Invalid card number format')
        return card_no
    
    @validator('cvv')
    def validate_cvv(cls, v):
        if not v.isdigit() or len(v) not in [3, 4]:
            raise ValueError('CVV must be 3 or 4 digits')
        return v
    
    class Config:
        from_attributes = True


# Request/Response Models
class BalanceRequest(BaseModel):
    """Balance check request"""
    account_no: str


class BalanceResponse(BaseModel):
    """Balance check response"""
    account_no: str
    account_type: str
    balance: float
    currency: str


class TransferRequest(BaseModel):
    """Money transfer request"""
    from_account: str
    to_account: str
    amount: float = Field(gt=0)
    description: Optional[str] = "Transfer"


class TransferResponse(BaseModel):
    """Money transfer response"""
    success: bool
    message: str
    transaction_id: Optional[int] = None
    new_balance: Optional[float] = None


class BillPaymentRequest(BaseModel):
    """Bill payment request"""
    user_id: int
    bill_type: BillType
    amount: float = Field(gt=0)
    account_no: str


class BillPaymentResponse(BaseModel):
    """Bill payment response"""
    success: bool
    message: str
    transaction_id: Optional[int] = None
    new_balance: Optional[float] = None


class TransactionHistoryRequest(BaseModel):
    """Transaction history request"""
    account_no: str
    limit: int = Field(default=10, le=50)


class TransactionHistoryResponse(BaseModel):
    """Transaction history response"""
    account_no: str
    transactions: List[Transaction]


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "DATABASE MODELS TEST")
    print("=" * 70)
    
    # Test User model
    print("\n👤 Testing User Model:")
    print("-" * 70)
    user = User(
        id=1,
        name="Ali Khan",
        phone="03001234567",
        email="ali@email.com"
    )
    print(f"User: {user.name} ({user.phone})")
    print(f"Valid: ✅")
    
    # Test Account model
    print("\n🏦 Testing Account Model:")
    print("-" * 70)
    account = Account(
        id=1,
        user_id=1,
        account_no="PK12ABCD1234567890123456",
        account_type=AccountType.SAVINGS,
        balance=125450.00,
        currency="PKR"
    )
    print(f"Account: {account.account_no}")
    print(f"Type: {account.account_type.value}")
    print(f"Balance: PKR {account.balance:,.2f}")
    print(f"Valid: ✅")
    
    # Test Transaction model
    print("\n💳 Testing Transaction Model:")
    print("-" * 70)
    transaction = Transaction(
        id=1,
        account_id=1,
        type=TransactionType.DEBIT,
        amount=5000.00,
        description="ATM Withdrawal",
        balance_after=120450.00
    )
    print(f"Transaction: {transaction.type.value}")
    print(f"Amount: PKR {transaction.amount:,.2f}")
    print(f"Valid: ✅")
    
    # Test Bill model
    print("\n🧾 Testing Bill Model:")
    print("-" * 70)
    bill = Bill(
        id=1,
        user_id=1,
        type=BillType.ELECTRICITY,
        amount=4200.00,
        due_date=date.today(),
        reference_no="LESCO-2024-001"
    )
    print(f"Bill: {bill.type.value}")
    print(f"Amount: PKR {bill.amount:,.2f}")
    print(f"Status: {bill.status.value}")
    print(f"Valid: ✅")
    
    # Test validation
    print("\n✅ Testing Validation:")
    print("-" * 70)
    
    try:
        # This should fail - negative balance
        invalid_account = Account(
            user_id=1,
            account_no="PK12ABCD1234567890123456",
            account_type=AccountType.SAVINGS,
            balance=-100.00
        )
    except Exception as e:
        print(f"❌ Caught validation error (expected): {str(e)}")
    
    try:
        # This should fail - invalid card number
        invalid_card = Card(
            account_id=1,
            card_number="123",  # Too short
            card_type=CardType.DEBIT,
            card_name="Test",
            expiry_date=date.today(),
            cvv="123"
        )
    except Exception as e:
        print(f"❌ Caught validation error (expected): {str(e)}")
    
    print("\n" + "=" * 70)
    print("✅ Database models validation complete!")