"""
Core layers for the bank teller chatbot redesign
Phase 1: Complete system redesign with 5 new architectural layers

This module provides:
- validation_layer: Input validation and rate limiting
- state_machine: Dialogue state management with explicit states
- transaction_manager: Idempotency, audit logging, and transactions
- error_recovery: Error handling with recovery paths
"""

# Import all core components
from .validation_layer import (
    RequestValidator,
    RateLimiter,
    rate_limiter,
    request_validator,
)

from .state_machine import (
    DialogueStateEnum,
    DialogueState,
    StateMachine,
)

from .transaction_manager import (
    TransactionStatus,
    AuditLogEntry,
    TransactionManager,
)

from .error_recovery import (
    ErrorType,
    ErrorResponse,
    ErrorRecovery,
)

__all__ = [
    # Validation layer
    "RequestValidator",
    "RateLimiter",
    "rate_limiter",
    "request_validator",
    
    # State machine
    "DialogueStateEnum",
    "DialogueState",
    "StateMachine",
    
    # Transaction manager
    "TransactionStatus",
    "AuditLogEntry",
    "TransactionManager",
    
    # Error recovery
    "ErrorType",
    "ErrorResponse",
    "ErrorRecovery",
]

__version__ = "1.0.0"
__author__ = "Bank Teller Chatbot Team"
__description__ = "Core layers for bank teller chatbot redesign (Phase 1)"
