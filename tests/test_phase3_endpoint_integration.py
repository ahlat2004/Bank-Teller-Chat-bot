"""
Phase 3 Tests: Main Endpoint Refactoring with Core Layers
Tests the refactored /api/chat endpoint that integrates Phase 1 & Phase 2 core layers
"""

import pytest
import json
import uuid
import sys
import os

# Add paths for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_root, 'backend', 'app')
backend_dir = os.path.join(project_root, 'backend')

sys.path.insert(0, app_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

from app.core.validation_layer import RequestValidator, RateLimiter
from app.core.state_machine import StateMachine, DialogueStateEnum
from app.core.transaction_manager import TransactionManager
from app.core.error_recovery import ErrorRecovery, ErrorType
from app.database.db_manager import DatabaseManager


class TestPhase3EndpointIntegration:
    """Test Phase 3 refactored endpoint with core layers integration"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        import tempfile
        temp_file = tempfile.mktemp(suffix='.db')
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        db = DatabaseManager(temp_file)
        db.apply_phase2_migration()
        
        yield db
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    def test_state_machine_locks_intent_during_multi_turn(self):
        """Test that state machine prevents intent reclassification during multi-turn flow"""
        sm = StateMachine()
        sm.set_intent("create_account", confidence=0.95)
        assert sm.intent == "create_account"
        assert sm.is_intent_locked() is True
        
        sm.set_intent("transfer_money", confidence=0.90)
        assert sm.intent == "create_account", "Intent should remain locked during multi-turn"
    
    def test_rate_limiter_respects_per_user_limits(self):
        """Test that rate limiter applies per-user limits, not global"""
        limiter = RateLimiter()
        
        for i in range(10):
            limiter.track_request(user_id=1, session_id="session1")
        allowed1, _ = limiter.check_rate_limit(user_id=1, session_id="session1")
        assert not allowed1
        
        allowed2, _ = limiter.check_rate_limit(user_id=2, session_id="session2")
        assert allowed2
    
    def test_transaction_manager_creates_idempotency_keys(self, temp_db):
        """Test that transaction manager generates consistent idempotency keys"""
        tm = TransactionManager(temp_db)
        user_id = 1
        
        slots1 = {'amount': '100', 'to_account': '123', 'from_account': '456'}
        key1 = tm.generate_idempotency_key(user_id, "transfer_money", slots1)
        key2 = tm.generate_idempotency_key(user_id, "transfer_money", slots1)
        
        # Keys should have same hash prefix (content hash) but different UUID suffix
        # This is by design - each request gets unique key but same hash for detection
        assert key1.split('-')[0] == key2.split('-')[0], "Content hash should be consistent"
        
        # Different slots should produce different content hash
        slots2 = {'amount': '100', 'to_account': '789', 'from_account': '456'}
        key3 = tm.generate_idempotency_key(user_id, "transfer_money", slots2)
        assert key1.split('-')[0] != key3.split('-')[0], "Different slots should have different hash"
    
    def test_audit_logging_captures_all_interactions(self, temp_db):
        """Test that database audit logging captures user interactions"""
        user_id = 1
        idempotency_key = str(uuid.uuid4())
        session_id = "test_session_123"
        
        temp_db.log_audit(
            user_id=user_id,
            session_id=session_id,
            intent="check_balance",
            action="check_balance",
            input_data={},
            output_data={},
            status="success",
            idempotency_key=idempotency_key
        )
        
        audit_entry = temp_db.get_audit_by_idempotency(idempotency_key)
        assert audit_entry is not None
        assert audit_entry["user_id"] == user_id
        assert audit_entry["action"] == "check_balance"
        assert audit_entry["status"] == "success"
    
    def test_duplicate_request_detection_via_idempotency(self, temp_db):
        """Test that duplicate requests are detected via idempotency keys"""
        user_id = 1
        session_id = "test_session_dup"
        idempotency_key = "unique_key_123"
        
        temp_db.log_audit(
            user_id=user_id,
            session_id=session_id,
            intent="transfer_money",
            action="transfer_money",
            input_data={},
            output_data={},
            status="success",
            idempotency_key=idempotency_key
        )
        
        existing = temp_db.get_audit_by_idempotency(idempotency_key)
        assert existing is not None, "Duplicate should be detected"
        assert existing["action"] == "transfer_money"
    
    def test_session_persistence_in_database(self, temp_db):
        """Test that session state persists in Phase 2 database"""
        user_id = 1
        session_id = "persist_session_789"
        
        temp_db.create_session(user_id, session_id)
        session = temp_db.get_session(session_id)
        assert session is not None
        assert session["user_id"] == user_id
        assert session["id"] == session_id
        
        state_json = json.dumps({"intent": "check_balance", "slots": {}})
        temp_db.update_session_state(session_id, state_json, "check_balance")
        
        updated_session = temp_db.get_session(session_id)
        assert updated_session["state_json"] == state_json
        assert updated_session["current_intent"] == "check_balance"
    
    def test_validation_message_check(self):
        """Test message validation"""
        valid, msg = RequestValidator.validate_message("Send money to Ahmed")
        assert valid is True
        
        valid, msg = RequestValidator.validate_message("")
        assert valid is False
    
    def test_multi_layer_integration_complete_flow(self, temp_db):
        """Test complete flow through all layers: validate -> state -> transaction -> audit"""
        sm = StateMachine()
        tm = TransactionManager(db_manager=temp_db)
        
        user_id = 1
        session_id = "integration_flow_123"
        idempotency_key = str(uuid.uuid4())
        message = "I want to transfer 500 to account 123"
        
        # Validate
        valid, msg = RequestValidator.validate_message(message)
        assert valid
        
        # Intent + State
        sm.set_intent("transfer_money", confidence=0.95)
        sm.fill_slot("amount", "500")
        sm.fill_slot("to_account", "123")
        
        # Idempotency
        idempotency = tm.generate_idempotency_key(user_id, "transfer_money", sm.filled_slots)
        assert idempotency is not None
        
        # Database (session + audit)
        temp_db.create_session(user_id, session_id)
        temp_db.log_audit(
            user_id=user_id,
            session_id=session_id,
            action=sm.intent,
            intent=sm.intent,
            input_data={},
            output_data={},
            status="success",
            idempotency_key=idempotency_key
        )
        
        # Verify complete flow
        session = temp_db.get_session(session_id)
        assert session is not None
        
        audit = temp_db.get_audit_by_idempotency(idempotency_key)
        assert audit is not None
        assert audit["intent"] == "transfer_money"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
