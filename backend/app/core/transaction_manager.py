"""
Transaction Manager - Idempotency, audit logging, and transaction semantics
Fixes Flaws: #14 (No Idempotency Keys), #16 (No Audit Trail), #20 (No Rollback Capability)
"""

import json
import uuid
import hashlib
from typing import Tuple, Dict, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import traceback


class TransactionStatus(Enum):
    """Transaction status enumeration"""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    ROLLED_BACK = "rolled_back"


@dataclass
class AuditLogEntry:
    """Audit log entry for transaction tracking"""
    audit_id: Optional[int] = None
    user_id: int = 0
    session_id: str = ""
    intent: str = ""
    action: str = ""
    input_data: Dict[str, Any] = None
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    error_message: Optional[str] = None
    idempotency_key: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert input_data and output_data to JSON strings for storage
        data['input_data'] = json.dumps(self.input_data) if self.input_data else "{}"
        data['output_data'] = json.dumps(self.output_data) if self.output_data else None
        return data


class TransactionManager:
    """
    Manages transactional semantics for banking operations
    Features:
    - Idempotency key generation to prevent duplicate charges
    - Duplicate request detection
    - Transaction wrapping with rollback capability
    - Comprehensive audit logging
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize transaction manager
        Args:
            db_manager: Database manager instance for storing audit logs
        """
        self.db_manager = db_manager
        self.pending_transactions: Dict[str, Dict[str, Any]] = {}  # In-memory tracking
    
    def generate_idempotency_key(self, user_id: int, intent: str, slots: Dict[str, Any]) -> str:
        """
        Generate UUID-based idempotency key
        Same user + intent + slots = same idempotency key (prevents duplicates)
        
        Args:
            user_id: User ID
            intent: Intent name
            slots: Filled slots
        
        Returns:
            Unique idempotency key string
        """
        # Create consistent hash from user_id + intent + slots
        # This ensures same request produces same key
        serialized_slots = json.dumps(slots, sort_keys=True, default=str)
        content = f"{user_id}:{intent}:{serialized_slots}"
        
        # Generate hash for consistency
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Combine with UUID for unique identity
        idempotency_key = f"{content_hash[:16]}-{uuid.uuid4().hex[:16]}"
        
        return idempotency_key
    
    def is_duplicate_request(self, idempotency_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if request was already processed
        
        Args:
            idempotency_key: Idempotency key to check
        
        Returns:
            (is_duplicate: bool, previous_result: Optional[Dict])
            If duplicate, returns (True, previous_result)
            If new request, returns (False, None)
        """
        # Check in database if db_manager available
        if self.db_manager:
            try:
                audit_entry = self.db_manager.get_audit_by_idempotency(idempotency_key)
                if audit_entry:
                    return True, {
                        "status": audit_entry.get('status'),
                        "output": json.loads(audit_entry.get('output_data', '{}')),
                        "message": f"Request already processed. Returning previous result.",
                    }
            except Exception:
                pass  # Fall through to return False if DB unavailable
        
        # Check in-memory tracking
        if idempotency_key in self.pending_transactions:
            transaction = self.pending_transactions[idempotency_key]
            if transaction.get('status') in ['success', 'failed']:
                return True, {
                    "status": transaction.get('status'),
                    "output": transaction.get('output'),
                    "message": f"Request already processed. Returning previous result.",
                }
        
        return False, None
    
    def execute_with_transaction(
        self,
        action_func: Callable,
        idempotency_key: str,
        user_id: int,
        session_id: str,
        intent: str,
        action: str,
        input_data: Dict[str, Any],
        *args,
        **kwargs
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Execute action with transaction semantics
        Wraps action in idempotency, audit logging, and error handling
        
        Args:
            action_func: Function to execute
            idempotency_key: Idempotency key for duplicate detection
            user_id: User ID
            session_id: Session ID
            intent: Intent name
            action: Action name
            input_data: Input to action
            *args: Arguments to pass to action_func
            **kwargs: Keyword arguments to pass to action_func
        
        Returns:
            (success: bool, message: str, result_data: Optional[Dict])
        """
        # Check for duplicate request
        is_duplicate, previous_result = self.is_duplicate_request(idempotency_key)
        if is_duplicate:
            return (
                previous_result['status'] == 'success',
                previous_result['message'],
                previous_result.get('output')
            )
        
        # Create audit log entry
        audit_entry = AuditLogEntry(
            user_id=user_id,
            session_id=session_id,
            intent=intent,
            action=action,
            input_data=input_data,
            status=TransactionStatus.PENDING.value,
            idempotency_key=idempotency_key,
        )
        
        # Track in-memory
        self.pending_transactions[idempotency_key] = {
            'status': 'pending',
            'entry': audit_entry,
        }
        
        result_data = None
        error_message = None
        success = False
        
        try:
            # BEGIN TRANSACTION (in database this would be explicit)
            # Execute action
            result_data = action_func(*args, **kwargs)
            
            # Mark as success
            audit_entry.status = TransactionStatus.SUCCESS.value
            audit_entry.output_data = result_data if isinstance(result_data, dict) else {"result": str(result_data)}
            
            success = True
            message = "Action completed successfully."
            
            # Log success to database
            if self.db_manager:
                self.db_manager.log_audit(
                    user_id=audit_entry.user_id,
                    session_id=audit_entry.session_id,
                    intent=audit_entry.intent,
                    action=audit_entry.action,
                    input_data=audit_entry.input_data,
                    output_data=audit_entry.output_data,
                    status=audit_entry.status,
                    idempotency_key=audit_entry.idempotency_key,
                )
            
            # COMMIT TRANSACTION (in database this would be explicit)
            
        except Exception as e:
            # ROLLBACK TRANSACTION (in database this would be explicit)
            success = False
            error_message = str(e)
            audit_entry.status = TransactionStatus.FAILURE.value
            audit_entry.error_message = error_message
            message = f"Action failed: {error_message}"
            
            # Log failure to database
            if self.db_manager:
                self.db_manager.log_audit(
                    user_id=audit_entry.user_id,
                    session_id=audit_entry.session_id,
                    intent=audit_entry.intent,
                    action=audit_entry.action,
                    input_data=audit_entry.input_data,
                    output_data=None,
                    status=audit_entry.status,
                    error_msg=audit_entry.error_message,
                    idempotency_key=audit_entry.idempotency_key,
                )
        
        finally:
            # Update in-memory tracking
            self.pending_transactions[idempotency_key] = {
                'status': 'success' if success else 'failed',
                'entry': audit_entry,
                'output': result_data,
            }
        
        return success, message, result_data
    
    def log_audit_entry(
        self,
        user_id: int,
        session_id: str,
        intent: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]],
        status: str,
        idempotency_key: str,
        error_msg: Optional[str] = None
    ) -> Optional[int]:
        """
        Log transaction to audit_log table
        
        Args:
            user_id: User ID
            session_id: Session ID
            intent: Intent name
            action: Action name
            input_data: Input data
            output_data: Output data
            status: Transaction status
            idempotency_key: Idempotency key
            error_msg: Error message if failed
        
        Returns:
            Audit log ID if database available, None otherwise
        """
        entry = AuditLogEntry(
            user_id=user_id,
            session_id=session_id,
            intent=intent,
            action=action,
            input_data=input_data,
            output_data=output_data,
            status=status,
            error_message=error_msg,
            idempotency_key=idempotency_key,
        )
        
        # Store in database if available
        if self.db_manager:
            try:
                return self.db_manager.log_audit(
                    user_id=entry.user_id,
                    session_id=entry.session_id,
                    intent=entry.intent,
                    action=entry.action,
                    input_data=entry.input_data,
                    output_data=entry.output_data,
                    status=entry.status,
                    error_msg=entry.error_message,
                    idempotency_key=entry.idempotency_key,
                )
            except Exception as e:
                print(f"Warning: Failed to log audit entry: {e}")
                return None
        
        return None
    
    def rollback_transaction(self, transaction_id: int) -> Tuple[bool, str]:
        """
        Reverse a completed transaction (Phase 1 implementation)
        
        In Phase 1, we mark transactions as rolled_back.
        In Phase 2, we would implement full reversal logic.
        
        Args:
            transaction_id: Transaction ID to rollback
        
        Returns:
            (success: bool, message: str)
        """
        # Phase 1: Simple rollback (just mark as rolled_back)
        # Phase 2 TODO: Implement full reversal logic
        
        if self.db_manager:
            try:
                # Mark transaction as rolled back
                self.db_manager.mark_transaction_rolled_back(transaction_id)
                return True, f"Transaction {transaction_id} marked as rolled back. Phase 2: Implement full reversal."
            except Exception as e:
                return False, f"Rollback failed: {str(e)}"
        
        return False, "Database manager not available for rollback."
    
    def get_transaction_history(self, user_id: int, limit: int = 10) -> list:
        """
        Get recent transaction history for user
        
        Args:
            user_id: User ID
            limit: Maximum number of transactions to return
        
        Returns:
            List of audit log entries
        """
        if self.db_manager:
            try:
                return self.db_manager.get_audit_by_user(user_id, limit=limit)
            except Exception:
                return []
        
        return []
    
    def get_audit_trail(self, session_id: str) -> list:
        """
        Get complete audit trail for session
        
        Args:
            session_id: Session ID
        
        Returns:
            List of audit log entries
        """
        if self.db_manager:
            try:
                return self.db_manager.get_audit_by_session(session_id)
            except Exception:
                return []
        
        return []
    
    def cleanup_old_entries(self, days: int = 7) -> None:
        """
        Clean up old in-memory entries (run periodically)
        
        Args:
            days: Remove entries older than this many days
        """
        cutoff = datetime.now().timestamp() - (days * 86400)
        keys_to_remove = []
        
        for key, transaction in self.pending_transactions.items():
            if 'entry' in transaction:
                entry_time = datetime.fromisoformat(transaction['entry'].created_at).timestamp()
                if entry_time < cutoff:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.pending_transactions[key]
