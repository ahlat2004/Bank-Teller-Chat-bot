"""
Phase 1 Core Layers - Unit Tests
Tests for validation_layer, state_machine, transaction_manager, and error_recovery
"""

import pytest
import json
from datetime import datetime, timedelta
from backend.app.core import (
    RequestValidator,
    RateLimiter,
    DialogueStateEnum,
    DialogueState,
    StateMachine,
    TransactionManager,
    TransactionStatus,
    ErrorType,
    ErrorRecovery,
)


class TestRequestValidator:
    """Test RequestValidator class"""
    
    def test_valid_message(self):
        """Test valid message validation"""
        valid, msg = RequestValidator.validate_message("Send money to Ahmed")
        assert valid is True
        assert msg == ""
    
    def test_empty_message(self):
        """Test empty message rejection"""
        valid, msg = RequestValidator.validate_message("")
        assert valid is False
        assert "empty" in msg.lower()
    
    def test_message_too_long(self):
        """Test message length limit"""
        long_msg = "a" * 1001
        valid, msg = RequestValidator.validate_message(long_msg)
        assert valid is False
        assert "too long" in msg.lower()
    
    def test_sql_injection_prevention(self):
        """Test SQL injection pattern removal"""
        malicious = "'; DROP TABLE users; --"
        sanitized = RequestValidator.sanitize_sql_injection(malicious)
        assert "DROP TABLE" not in sanitized
    
    def test_xss_prevention(self):
        """Test XSS pattern removal"""
        malicious = "<script>alert('XSS')</script>"
        sanitized = RequestValidator.sanitize_xss(malicious)
        assert "<script>" not in sanitized


class TestRateLimiter:
    """Test RateLimiter class"""
    
    def setup_method(self):
        """Reset rate limiter before each test"""
        self.limiter = RateLimiter()
    
    def test_first_request_allowed(self):
        """Test that first request is always allowed"""
        allowed, msg = self.limiter.check_rate_limit(user_id=1, session_id="session1")
        assert allowed is True
        assert msg == ""
    
    def test_per_minute_limit(self):
        """Test per-minute rate limiting"""
        for i in range(10):
            allowed, msg = self.limiter.check_rate_limit(user_id=1, session_id="session1")
            self.limiter.track_request(user_id=1, session_id="session1")
            assert allowed is True
        
        # 11th request should be rejected
        allowed, msg = self.limiter.check_rate_limit(user_id=1, session_id="session1")
        assert allowed is False
        assert "Too many requests" in msg
    
    def test_different_users_independent_limits(self):
        """Test that different users have independent rate limits"""
        for i in range(10):
            self.limiter.track_request(user_id=1, session_id="session1")
        
        # User 2 should not be affected by user 1's requests
        allowed, msg = self.limiter.check_rate_limit(user_id=2, session_id="session2")
        assert allowed is True


class TestStateMachine:
    """Test StateMachine class"""
    
    def test_initial_state_is_idle(self):
        """Test initial state is IDLE"""
        sm = StateMachine()
        assert sm.current_state == DialogueStateEnum.IDLE
    
    def test_set_intent_locks(self):
        """Test that setting intent locks it"""
        sm = StateMachine()
        sm.set_intent("create_account", confidence=0.99)
        
        assert sm.intent == "create_account"
        assert sm.is_intent_locked() is True
        
        # Try to set new intent - should fail
        result = sm.set_intent("check_balance", confidence=0.95)
        assert result is False
        assert sm.intent == "create_account"  # Still the old intent
    
    def test_intent_determines_slots(self):
        """Test that intent determines required slots"""
        sm = StateMachine()
        sm.set_intent("create_account")
        
        missing = sm.get_missing_slots()
        assert "name" in missing
        assert "phone" in missing
        assert "email" in missing
        assert "account_type" in missing
    
    def test_fill_slots(self):
        """Test slot filling"""
        sm = StateMachine()
        sm.set_intent("create_account")
        
        sm.fill_slot("name", "Ahmed")
        sm.fill_slot("phone", "03001234567")
        
        assert sm.filled_slots["name"] == "Ahmed"
        assert sm.filled_slots["phone"] == "03001234567"
        
        missing = sm.get_missing_slots()
        assert "name" not in missing
        assert "phone" not in missing
        assert "email" in missing
        assert "account_type" in missing
    
    def test_valid_state_transitions(self):
        """Test valid state transitions"""
        sm = StateMachine()
        
        # IDLE -> INTENT_CLASSIFIED
        assert sm.transition_to(DialogueStateEnum.INTENT_CLASSIFIED) is True
        
        # INTENT_CLASSIFIED -> SLOTS_FILLING
        assert sm.transition_to(DialogueStateEnum.SLOTS_FILLING) is True
        
        # SLOTS_FILLING -> CONFIRMATION_PENDING
        assert sm.transition_to(DialogueStateEnum.CONFIRMATION_PENDING) is True
    
    def test_invalid_state_transitions(self):
        """Test that invalid transitions are rejected"""
        sm = StateMachine()
        
        # Cannot go from IDLE to COMPLETED
        result = sm.transition_to(DialogueStateEnum.COMPLETED)
        assert result is False
        assert sm.current_state == DialogueStateEnum.IDLE
    
    def test_get_next_missing_slot(self):
        """Test getting next slot in order"""
        sm = StateMachine()
        sm.set_intent("create_account")
        
        next_slot = sm.get_next_missing_slot()
        assert next_slot == "name"
        
        sm.fill_slot("name", "Ahmed")
        next_slot = sm.get_next_missing_slot()
        assert next_slot == "phone"


class TestTransactionManager:
    """Test TransactionManager class"""
    
    def setup_method(self):
        """Initialize transaction manager before each test"""
        self.tm = TransactionManager()
    
    def test_idempotency_key_generation(self):
        """Test idempotency key generation"""
        key1 = self.tm.generate_idempotency_key(
            user_id=1,
            intent="transfer_money",
            slots={"amount": 5000, "to_account": "12345"}
        )
        
        key2 = self.tm.generate_idempotency_key(
            user_id=1,
            intent="transfer_money",
            slots={"amount": 5000, "to_account": "12345"}
        )
        
        # Different keys (UUID differs) but same hash prefix
        assert key1 != key2
        assert key1[:16] == key2[:16]  # Hash prefix is same
    
    def test_different_slots_different_hash(self):
        """Test that different slots produce different hashes"""
        key1 = self.tm.generate_idempotency_key(
            user_id=1,
            intent="transfer_money",
            slots={"amount": 5000}
        )
        
        key2 = self.tm.generate_idempotency_key(
            user_id=1,
            intent="transfer_money",
            slots={"amount": 6000}
        )
        
        assert key1[:16] != key2[:16]  # Different hash prefixes
    
    def test_duplicate_detection(self):
        """Test duplicate request detection"""
        key = "test-idempotency-key"
        
        # First request - should not be duplicate
        is_dup, result = self.tm.is_duplicate_request(key)
        assert is_dup is False
        assert result is None
        
        # Track the request
        self.tm.pending_transactions[key] = {
            'status': 'success',
            'output': {'result': 'success'},
        }
        
        # Second request with same key - should be duplicate
        is_dup, result = self.tm.is_duplicate_request(key)
        assert is_dup is True
        assert result is not None
    
    def test_execute_with_transaction_success(self):
        """Test transaction execution on success"""
        def sample_action(**kwargs):
            amount = kwargs.get('amount', 0)
            return {"charged": amount, "status": "success"}
        
        success, msg, result = self.tm.execute_with_transaction(
            action_func=sample_action,
            idempotency_key="test-key-1",
            user_id=1,
            session_id="session1",
            intent="pay_bill",
            action="charge",
            input_data={"amount": 1000},
            amount=1000
        )
        
        assert success is True
        assert result is not None
    
    def test_execute_with_transaction_failure(self):
        """Test transaction execution on failure"""
        def failing_action():
            raise ValueError("Insufficient balance")
        
        success, msg, result = self.tm.execute_with_transaction(
            action_func=failing_action,
            idempotency_key="test-key-fail",
            user_id=1,
            session_id="session1",
            intent="transfer_money",
            action="transfer",
            input_data={"amount": 50000},
        )
        
        assert success is False
        assert "Insufficient balance" in msg


class TestErrorRecovery:
    """Test ErrorRecovery class"""
    
    def test_validation_error(self):
        """Test validation error response"""
        error = ErrorRecovery.validation_error(
            field="email",
            value="invalid-email",
            reason="Invalid email format"
        )
        
        assert error.error_type == ErrorType.VALIDATION_ERROR
        assert "Invalid email" in error.message
        assert len(error.recovery_suggestions) > 0
    
    def test_insufficient_balance_error(self):
        """Test insufficient balance error"""
        error = ErrorRecovery.insufficient_balance_error(
            account_type="Checking",
            available=1000.0,
            requested=5000.0
        )
        
        assert error.error_type == ErrorType.BUSINESS_LOGIC_ERROR
        assert "1000" in error.message
        assert "5000" in error.message
        assert "4000" in error.message  # Shortfall
    
    def test_account_not_found_error(self):
        """Test account not found error"""
        accounts = [
            {"account_no": "1001", "type": "Checking", "balance": 5000},
            {"account_no": "1002", "type": "Savings", "balance": 10000},
        ]
        
        error = ErrorRecovery.account_not_found_error(
            account_identifier="1003",
            available_accounts=accounts
        )
        
        assert error.error_type == ErrorType.BUSINESS_LOGIC_ERROR
        assert "1001" in error.message
        assert "1002" in error.message
        assert "1003" in error.message
    
    def test_rate_limit_error(self):
        """Test rate limit error"""
        error = ErrorRecovery.rate_limit_error(
            limit_type="minute",
            reset_in=30
        )
        
        assert error.error_type == ErrorType.RATE_LIMIT_ERROR
        assert "30" in error.message
        assert len(error.recovery_suggestions) > 0
    
    def test_system_error(self):
        """Test system error"""
        error = ErrorRecovery.system_error(
            action="processing transfer",
            error_details="Database connection timeout"
        )
        
        assert error.error_type == ErrorType.SYSTEM_ERROR
        assert "processing transfer" in error.message
        assert len(error.recovery_suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
