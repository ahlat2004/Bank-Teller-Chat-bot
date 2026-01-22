"""
Phase 1 & 2 Integration Tests
Tests the core layers (Phase 1) with database operations (Phase 2)
"""

import pytest
import json
import os
import tempfile
from datetime import datetime

from backend.app.core import (
    RequestValidator,
    RateLimiter,
    DialogueStateEnum,
    StateMachine,
    TransactionManager,
    ErrorRecovery,
)
from backend.app.database.db_manager import DatabaseManager


class TestPhase1Phase2Integration:
    """Integration tests for Phase 1 and Phase 2"""
    
    @pytest.fixture(scope="function")
    def temp_db(self):
        """Create temporary database for testing"""
        # Create temp file
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        # Delete the empty file so DatabaseManager can create it fresh
        os.remove(path)
        
        # Initialize DB - this will create the schema
        db = DatabaseManager(path)
        
        # Apply Phase 2 migration
        db.apply_phase2_migration()
        
        # Seed with test data
        db.seed_database()
        
        yield db
        
        # Cleanup
        try:
            os.remove(path)
        except:
            pass
    
    def test_complete_dialogue_flow_with_audit(self, temp_db):
        """Test complete dialogue flow from validation through audit logging"""
        # Initialize components
        validator = RequestValidator()
        rate_limiter = RateLimiter()
        state_machine = StateMachine()
        transaction_manager = TransactionManager(db_manager=temp_db)
        
        # Create a test user
        user_id = 1
        session_id = "test_session_123"
        
        # ===== Step 1: User sends message =====
        message = "I want to check my balance"
        
        # Validate
        valid, msg = validator.validate_message(message)
        assert valid is True
        
        # Rate limit
        allowed, msg = rate_limiter.check_rate_limit(user_id, session_id)
        assert allowed is True
        rate_limiter.track_request(user_id, session_id)
        
        # ===== Step 2: State machine processes intent =====
        state_machine.set_intent("check_balance", confidence=0.98)
        assert state_machine.intent == "check_balance"
        assert state_machine.is_intent_locked() is True
        
        # ===== Step 3: Fill slots =====
        state_machine.fill_slot("account_type", "savings")
        assert state_machine.filled_slots["account_type"] == "savings"
        
        # ===== Step 4: Execute with transaction manager =====
        idempotency_key = transaction_manager.generate_idempotency_key(
            user_id=user_id,
            intent="check_balance",
            slots={"account_type": "savings"}
        )
        
        def check_balance_action():
            # Simulate getting balance from DB
            accounts = temp_db.get_user_accounts(user_id)
            if accounts:
                return {
                    "account_type": "savings",
                    "balance": accounts[0]["balance"],
                    "status": "success"
                }
            return {"status": "error", "message": "No accounts found"}
        
        success, msg, result = transaction_manager.execute_with_transaction(
            action_func=check_balance_action,
            idempotency_key=idempotency_key,
            user_id=user_id,
            session_id=session_id,
            intent="check_balance",
            action="get_balance",
            input_data={"account_type": "savings"}
        )
        
        assert success is True
        assert result is not None
        assert result["status"] == "success"
        
        # ===== Step 5: Verify audit log =====
        audit_entry = temp_db.get_audit_by_idempotency(idempotency_key)
        assert audit_entry is not None
        assert audit_entry["intent"] == "check_balance"
        assert audit_entry["status"] == "success"
        assert audit_entry["user_id"] == user_id
        
        # ===== Step 6: Test duplicate detection =====
        is_dup, prev_result = transaction_manager.is_duplicate_request(idempotency_key)
        assert is_dup is True
        assert prev_result is not None
        assert prev_result["status"] == "success"
    
    def test_validation_error_flow_with_audit(self, temp_db):
        """Test validation error handling with audit logging"""
        validator = RequestValidator()
        transaction_manager = TransactionManager(db_manager=temp_db)
        error_recovery = ErrorRecovery()
        
        user_id = 1
        session_id = "test_session_456"
        
        # ===== Step 1: Invalid input =====
        invalid_message = "a" * 1001  # Too long
        valid, msg = validator.validate_message(invalid_message)
        assert valid is False
        
        # ===== Step 2: Generate error recovery response =====
        error_response = error_recovery.validation_error(
            field="message",
            value=invalid_message[:50] + "...",
            reason="Message exceeds maximum length of 1000 characters"
        )
        
        assert error_response.error_type.value == "validation_error"
        assert len(error_response.recovery_suggestions) > 0
        
        # ===== Step 3: Log failed transaction =====
        idempotency_key = "test_validation_error_key"
        audit_id = temp_db.log_audit(
            user_id=user_id,
            session_id=session_id,
            intent="unknown",
            action="validate_input",
            input_data={"message": invalid_message[:50]},
            output_data=None,
            status="failure",
            idempotency_key=idempotency_key,
            error_msg="Message too long"
        )
        
        assert audit_id is not None
        
        # ===== Step 4: Retrieve audit log =====
        audit_entry = temp_db.get_audit_by_idempotency(idempotency_key)
        assert audit_entry is not None
        assert audit_entry["status"] == "failure"
    
    def test_session_state_persistence(self, temp_db):
        """Test session state persistence across requests"""
        state_machine = StateMachine()
        user_id = 1
        session_id = "persistent_session_123"
        
        # Create session first
        temp_db.create_session(user_id, session_id)
        
        # ===== Request 1: Set intent and fill first slot =====
        state_machine.set_intent("create_account", confidence=0.95)
        state_machine.fill_slot("name", "Ahmed Ali")
        
        # Save state to DB
        state_dict = state_machine.save_state()
        state_json = json.dumps(state_dict)
        temp_db.update_session_state(session_id, state_json, "create_account")
        
        # ===== Request 2: Restore state and continue =====
        state_machine2 = StateMachine()
        session_data = temp_db.get_session(session_id)
        
        assert session_data is not None
        assert session_data["current_intent"] == "create_account"
        
        # Restore state
        restored_state = json.loads(session_data["state_json"])
        state_machine2.restore_state(restored_state)
        
        # Verify restored state
        assert state_machine2.intent == "create_account"
        assert state_machine2.filled_slots["name"] == "Ahmed Ali"
        assert state_machine2.is_intent_locked() is True
        
        # Continue filling slots
        state_machine2.fill_slot("phone", "03001234567")
        assert state_machine2.filled_slots["phone"] == "03001234567"
    
    def test_multi_turn_dialogue_with_intent_locking(self, temp_db):
        """Test multi-turn dialogue with intent locking preventing reclassification"""
        validator = RequestValidator()
        rate_limiter = RateLimiter()
        state_machine = StateMachine()
        transaction_manager = TransactionManager(db_manager=temp_db)
        
        user_id = 1
        session_id = "multiturn_session"
        
        # ===== Turn 1: User starts create account =====
        message1 = "I want to create a new account"
        valid, _ = validator.validate_message(message1)
        assert valid is True
        
        state_machine.set_intent("create_account", confidence=0.99)
        state_machine.fill_slot("name", "Ahmed")
        
        # Log first turn
        idempotency_key1 = transaction_manager.generate_idempotency_key(
            user_id, "create_account", {"name": "Ahmed"}
        )
        temp_db.log_audit(
            user_id, session_id, "create_account", "fill_slot",
            {"slot": "name", "value": "Ahmed"},
            {"status": "slot_filled"},
            "success", idempotency_key1
        )
        
        # ===== Turn 2: User provides phone (intent should NOT change) =====
        message2 = "My phone is 03001234567"
        valid, _ = validator.validate_message(message2)
        assert valid is True
        
        # Intent is locked - cannot reclassify
        result = state_machine.set_intent("check_balance", confidence=0.85)
        assert result is False  # Should fail to change intent
        assert state_machine.intent == "create_account"  # Intent unchanged
        
        # Fill phone slot
        state_machine.fill_slot("phone", "03001234567")
        
        # Log second turn
        idempotency_key2 = transaction_manager.generate_idempotency_key(
            user_id, "create_account", {"name": "Ahmed", "phone": "03001234567"}
        )
        temp_db.log_audit(
            user_id, session_id, "create_account", "fill_slot",
            {"slot": "phone", "value": "03001234567"},
            {"status": "slot_filled"},
            "success", idempotency_key2
        )
        
        # ===== Verify audit trail =====
        audit_trail = temp_db.get_audit_by_session(session_id)
        assert len(audit_trail) == 2
        assert audit_trail[0]["action"] == "fill_slot"
        assert audit_trail[1]["action"] == "fill_slot"
    
    def test_rate_limiting_with_audit(self, temp_db):
        """Test rate limiting with audit logging"""
        rate_limiter = RateLimiter()
        transaction_manager = TransactionManager(db_manager=temp_db)
        error_recovery = ErrorRecovery()
        
        user_id = 2
        session_id = "rate_limit_test"
        
        # Make 10 requests (at limit)
        for i in range(10):
            allowed, msg = rate_limiter.check_rate_limit(user_id, session_id)
            assert allowed is True
            rate_limiter.track_request(user_id, session_id)
        
        # 11th request should be rate limited
        allowed, msg = rate_limiter.check_rate_limit(user_id, session_id)
        assert allowed is False
        assert "Too many requests" in msg
        
        # Log the rate limit error
        error = error_recovery.rate_limit_error("minute", 30)
        assert error.error_type.value == "rate_limit_error"
        
        # Log to audit
        temp_db.log_audit(
            user_id=user_id,
            session_id=session_id,
            intent="unknown",
            action="rate_limit_exceeded",
            input_data={"requests_count": 11},
            output_data=None,
            status="failure",
            idempotency_key="rate_limit_test_key",
            error_msg="Rate limit exceeded"
        )
        
        # Verify audit entry
        audit_entry = temp_db.get_audit_by_user(user_id, limit=1)
        assert len(audit_entry) > 0
        assert audit_entry[0]["action"] == "rate_limit_exceeded"
    
    def test_transaction_with_insufficient_balance(self, temp_db):
        """Test transfer transaction with insufficient balance"""
        state_machine = StateMachine()
        transaction_manager = TransactionManager(db_manager=temp_db)
        error_recovery = ErrorRecovery()
        
        user_id = 1
        session_id = "transfer_test"
        
        # ===== Set up transfer intent =====
        state_machine.set_intent("transfer_money", confidence=0.97)
        state_machine.fill_slot("amount", 50000)  # Large amount
        state_machine.fill_slot("from_account", "savings")
        state_machine.fill_slot("to_account", "checking")
        state_machine.fill_slot("recipient_phone", "03009876543")
        
        # ===== Simulate transfer with insufficient balance =====
        def transfer_action():
            available = 5000.0
            requested = 50000.0
            if requested > available:
                raise ValueError(f"Insufficient balance. Available: {available}, Requested: {requested}")
            return {"status": "success"}
        
        idempotency_key = transaction_manager.generate_idempotency_key(
            user_id, "transfer_money",
            {"amount": 50000, "from_account": "savings", "to_account": "checking"}
        )
        
        success, msg, result = transaction_manager.execute_with_transaction(
            action_func=transfer_action,
            idempotency_key=idempotency_key,
            user_id=user_id,
            session_id=session_id,
            intent="transfer_money",
            action="transfer",
            input_data=state_machine.filled_slots
        )
        
        assert success is False
        assert "Insufficient balance" in msg
        
        # ===== Generate error recovery response =====
        error_response = error_recovery.insufficient_balance_error(
            account_type="savings",
            available=5000.0,
            requested=50000.0
        )
        
        assert error_response.error_type.value == "business_logic_error"
        assert "5000" in error_response.message
        assert len(error_response.recovery_suggestions) > 0
        
        # ===== Verify audit log shows failure =====
        audit_entry = temp_db.get_audit_by_idempotency(idempotency_key)
        assert audit_entry is not None
        assert audit_entry["status"] == "failure"
        assert "Insufficient balance" in audit_entry["error_message"]
    
    def test_idempotency_prevents_duplicate_charges(self, temp_db):
        """Test idempotency prevents processing same request twice"""
        transaction_manager = TransactionManager(db_manager=temp_db)
        
        user_id = 1
        session_id = "idempotency_test"
        slots = {"amount": 1000, "from_account": "savings", "to_account": "checking"}
        
        # Generate consistent idempotency key
        idempotency_key = transaction_manager.generate_idempotency_key(
            user_id, "transfer_money", slots
        )
        
        # Process count
        process_count = [0]
        
        def transfer_action():
            process_count[0] += 1
            return {"status": "success", "transaction_id": 101}
        
        # ===== Request 1: Process transfer =====
        success1, msg1, result1 = transaction_manager.execute_with_transaction(
            action_func=transfer_action,
            idempotency_key=idempotency_key,
            user_id=user_id,
            session_id=session_id,
            intent="transfer_money",
            action="transfer",
            input_data=slots
        )
        
        assert success1 is True
        assert process_count[0] == 1  # Action executed once
        
        # ===== Request 2: Same request (same idempotency key) =====
        success2, msg2, result2 = transaction_manager.execute_with_transaction(
            action_func=transfer_action,
            idempotency_key=idempotency_key,
            user_id=user_id,
            session_id=session_id,
            intent="transfer_money",
            action="transfer",
            input_data=slots
        )
        
        assert success2 is True
        assert process_count[0] == 1  # Action NOT executed again
        assert result1 == result2  # Same result returned
        assert msg2 == "Request already processed. Returning previous result."
    
    def test_complete_user_audit_trail(self, temp_db):
        """Test retrieving complete audit trail for a user"""
        transaction_manager = TransactionManager(db_manager=temp_db)
        user_id = 1
        session_id = "audit_trail_test"
        
        # Log multiple actions
        actions = [
            ("check_balance", "get_balance", "success", {"account": "savings"}),
            ("create_account", "fill_slot", "success", {"field": "name"}),
            ("transfer_money", "validate_amount", "failure", {"amount": 50000}),
        ]
        
        for i, (intent, action, status, input_data) in enumerate(actions):
            idempotency_key = f"test_key_{i}"
            temp_db.log_audit(
                user_id=user_id,
                session_id=session_id,
                intent=intent,
                action=action,
                input_data=input_data,
                output_data={"result": status},
                status=status,
                idempotency_key=idempotency_key,
                error_msg="Insufficient balance" if status == "failure" else None
            )
        
        # Retrieve audit trail
        audit_trail = temp_db.get_audit_by_user(user_id, limit=10)
        
        assert len(audit_trail) >= 3
        
        # Verify all actions are present
        intents = [entry["intent"] for entry in audit_trail]
        assert "check_balance" in intents
        assert "create_account" in intents
        assert "transfer_money" in intents


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
