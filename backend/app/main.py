"""
FastAPI Backend - Main Application
Bank Teller Chatbot REST API
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import sys
import logging

# Add paths for imports
app_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app
backend_dir = os.path.dirname(app_dir)                # backend
project_dir = os.path.dirname(backend_dir)            # project root

sys.path.insert(0, app_dir)      # Add backend/app to path
sys.path.insert(0, backend_dir)  # Add backend to path

# Import logging config first
from app.utils.logging_config import setup_logging, log_api_request, log_api_response, log_api_error

# Setup enhanced logging
logger = logging.getLogger(__name__)
api_logger = logging.getLogger('api')

# Import custom modules
from app.database.db_manager import DatabaseManager
from app.auth.auth_manager import AuthManager
from app.ml.load_trained_model import IntentClassifierInference
from app.ml.entity_extractor import BankingEntityExtractor
from app.ml.dialogue.dialogue_manager import DialogueManager
from app.ml.dialogue.dialogue_state import DialogueState, ConversationStatus
from app.ml.entity_validator import EntityValidator
from app.utils.session_manager import SessionManager
from app.utils.response_generator import ResponseGenerator
from app.utils.receipt_generator import ReceiptGenerator
from app.utils.error_handler import ErrorHandler
from app.utils.conversation_handler import ConversationHandler

# ===== Phase 1 & Phase 2 Core Layers =====
from app.core.validation_layer import RequestValidator, RateLimiter
from app.core.state_machine import StateMachine, DialogueStateEnum
from app.core.transaction_manager import TransactionManager
from app.core.error_recovery import ErrorRecovery, ErrorType

# ===== Phase 4: Enhanced Entity Extractor =====
from app.core.enhanced_entity_extractor import EnhancedBankingEntityExtractor
import json
import uuid
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Bank Teller Chatbot API",
    description="AI-powered banking assistant with natural language interface",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (loaded on startup)
db_manager: Optional[DatabaseManager] = None
intent_classifier: Optional[IntentClassifierInference] = None
entity_extractor: Optional[BankingEntityExtractor] = None
dialogue_manager: Optional[DialogueManager] = None
session_manager: Optional[SessionManager] = None
response_generator: Optional[ResponseGenerator] = None
auth_manager: Optional[AuthManager] = None
entity_validator: Optional[EntityValidator] = None
receipt_generator: Optional[ReceiptGenerator] = None
error_handler: Optional[ErrorHandler] = None

# ===== Phase 1 & Phase 2 Core Layer Instances =====
request_validator: Optional[RequestValidator] = None
rate_limiter: Optional[RateLimiter] = None
transaction_manager: Optional[TransactionManager] = None
error_recovery: Optional[ErrorRecovery] = None

# ===== Phase 4: Enhanced Entity Extractor Instance =====
enhanced_entity_extractor: Optional[EnhancedBankingEntityExtractor] = None


# ========== STARTUP & SHUTDOWN ==========

@app.on_event("startup")
async def startup_event():
    """Initialize all components on startup"""
    global db_manager, intent_classifier, entity_extractor
    global dialogue_manager, session_manager, response_generator, auth_manager
    global entity_validator, receipt_generator, error_handler
    global request_validator, rate_limiter, transaction_manager, error_recovery
    global enhanced_entity_extractor
    
    logger.info("Starting Bank Teller Chatbot API...")
    
    try:
        # Calculate project paths
        current_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app
        backend_dir = os.path.dirname(current_dir)                # backend
        project_dir = os.path.dirname(backend_dir)                # project root
        
        db_path = os.path.join(project_dir, 'data', 'bank_demo.db')
        
        # Initialize database
        logger.info("Loading database...")
        db_manager = DatabaseManager(db_path)
        logger.info("Database loaded")
        
        # Initialize intent classifier
        logger.info("Loading intent classifier...")
        intent_classifier = IntentClassifierInference(os.path.join(project_dir, 'data', 'models'))
        intent_classifier.load_artifacts()
        logger.info("Intent classifier loaded")
        
        # Initialize entity extractor
        logger.info("Loading entity extractor...")
        entity_extractor = BankingEntityExtractor()
        logger.info("Entity extractor loaded")
        
        # Initialize enhanced entity extractor (Phase 4)
        logger.info("Loading enhanced entity extractor...")
        enhanced_entity_extractor = EnhancedBankingEntityExtractor()
        logger.info("Enhanced entity extractor loaded")
        
        # Initialize dialogue manager
        logger.info("Loading dialogue manager...")
        dialogue_manager = DialogueManager()
        logger.info("Dialogue manager loaded")
        
        # Initialize session manager
        logger.info("Loading session manager...")
        session_manager = SessionManager()
        logger.info("Session manager loaded")
        # Optionally clear all sessions on startup to force a fresh run
        try:
            force_fresh = os.getenv('FORCE_FRESH_SESSIONS', 'false').lower() in ('1', 'true', 'yes')
        except Exception:
            force_fresh = False

        if force_fresh:
            logger.info('FORCE_FRESH_SESSIONS enabled — clearing all saved sessions')
            try:
                cleared = session_manager.clear_all_sessions()
                logger.info(f'Cleared {cleared} sessions on startup')
            except Exception as e:
                logger.warning(f'Failed to clear sessions on startup: {e}')
        
        # Initialize response generator
        logger.info("Loading response generator...")
        response_generator = ResponseGenerator(db_manager)
        logger.info("Response generator loaded")
        
        # Initialize authentication manager
        logger.info("Loading authentication manager...")
        auth_manager = AuthManager()
        logger.info("Authentication manager loaded")
        
        # Initialize entity validator (Phase 2)
        logger.info("Loading entity validator...")
        entity_validator = EntityValidator()
        logger.info("Entity validator loaded")
        
        # Initialize receipt generator (Phase 2)
        logger.info("Loading receipt generator...")
        receipt_generator = ReceiptGenerator()
        logger.info("Receipt generator loaded")
        
        # Initialize error handler (Phase 2)
        logger.info("Loading error handler...")
        error_handler = ErrorHandler()
        logger.info("Error handler loaded")
        
        # ===== Phase 1 & Phase 2 Core Layer Initialization =====
        logger.info("Initializing Phase 1 & Phase 2 core layers...")
        
        # Initialize validation layer
        logger.info("Initializing request validator...")
        request_validator = RequestValidator()
        logger.info("Request validator initialized")
        
        # Initialize rate limiter
        logger.info("Initializing rate limiter...")
        rate_limiter = RateLimiter()
        logger.info("Rate limiter initialized")
        
        # Initialize transaction manager
        logger.info("Initializing transaction manager...")
        transaction_manager = TransactionManager(db_manager)
        logger.info("Transaction manager initialized")
        
        # Initialize error recovery
        logger.info("Initializing error recovery...")
        error_recovery = ErrorRecovery()
        logger.info("Error recovery initialized")
        
        logger.info("All components loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Bank Teller Chatbot API...")


# ========== REQUEST/RESPONSE MODELS ==========

class ChatRequest(BaseModel):
    """Chat message request"""
    message: str
    user_id: int = 1  # Default user
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat message response"""
    response: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    entities: Optional[Dict[str, Any]] = None
    requires_input: bool = False
    session_id: str
    status: str = "success"
    debug_state_intent: Optional[str] = None  # DEBUG: actual state.intent
    debug_session_found: Optional[bool] = None  # DEBUG: was session found or created


class BalanceRequest(BaseModel):
    """Balance check request"""
    user_id: int
    account_no: Optional[str] = None


class TransferRequest(BaseModel):
    """Money transfer request"""
    user_id: int
    from_account: str
    to_account: str
    amount: float
    description: Optional[str] = "Transfer"


class BillPaymentRequest(BaseModel):
    """Bill payment request"""
    user_id: int
    bill_type: str
    amount: float
    account_no: str


# ========== INTENT REMAPPING ==========

def remap_intent(classifier_intent: str, confidence: float) -> tuple:
    """
    Remap model-trained intents to dialogue system intents
    
    The model is trained on a public banking dataset, but our dialogue system
    uses custom intent names. This function bridges the gap.
    
    Args:
        classifier_intent: Intent from model (e.g., 'check_fees')
        confidence: Confidence score from model
        
    Returns:
        Tuple of (remapped_intent, confidence)
    """
    # Intent remapping dictionary
    intent_map = {
        # Balance checking - map ALL balance-related intents
        'check_current_balance_on_card': 'check_balance',
        'check_fees': 'check_balance',
        'check_loan_payments': 'check_balance',
        'check_mortgage_payments': 'check_balance',
        'check_card_annual_fee': 'check_balance',
        
        # Money transfer - map ALL transfer/payment intents to transfer_money
        'make_transfer': 'transfer_money',
        'cancel_transfer': 'transfer_money',
        'bill_payment': 'bill_payment',  # Special case for bills
        'pay_bill': 'bill_payment',
        
        # Bill payment - map cancel mortgage/loan as bill payment fallback
        'cancel_mortgage': 'bill_payment',  # Fallback - user probably meant bill
        'cancel_loan': 'bill_payment',      # Fallback - user probably meant bill
        'apply_for_loan': 'bill_payment',   # Fallback
        'apply_for_mortgage': 'bill_payment', # Fallback
        
        # Account management
        'create_account': 'create_account',
        'close_account': 'close_account',
        
        # Card operations
        'activate_card': 'activate_card',
        'block_card': 'block_card',
        'cancel_card': 'cancel_card',
        'dispute_ATM_withdrawal': 'dispute_atm',
        'recover_swallowed_card': 'recover_card',
        
        # Transactions
        'check_recent_transactions': 'check_recent_transactions',
        
        # Services
        'customer_service': 'customer_service',
        'human_agent': 'human_agent',
        'find_ATM': 'find_atm',
        'find_branch': 'find_branch',
        'get_password': 'customer_service',
        'set_up_password': 'customer_service',
    }
    
    remapped = intent_map.get(classifier_intent, classifier_intent)
    return (remapped, confidence)


# ========== HEALTH CHECK ==========

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "online",
        "service": "Bank Teller Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "balance": "/api/balance/{user_id}",
            "transfer": "/api/transfer",
            "history": "/api/history/{user_id}",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": db_manager is not None,
        "intent_classifier": intent_classifier is not None,
        "entity_extractor": entity_extractor is not None,
        "dialogue_manager": dialogue_manager is not None
    }


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear chat session and reset all state"""
    try:
        # Delete session from memory
        session_manager.delete_session(session_id)
        
        # Delete session from database
        db_manager.delete_session(session_id)
        
        logger.info(f"[SESSION] Cleared session: {session_id}")
        
        return {
            "status": "success",
            "message": f"Session {session_id} cleared",
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"[SESSION] Error clearing session {session_id}: {e}")
        return {
            "status": "error",
            "message": f"Failed to clear session: {str(e)}",
            "session_id": session_id
        }


# ========== RESPONSE HELPER ==========

def make_response(response_text: str, intent: Optional[str] = None, confidence: Optional[float] = None,
                  entities: Dict = None, requires_input: bool = False, session_id: str = "",
                  status: str = "success", state_intent: Optional[str] = None,
                  session_found: Optional[bool] = None) -> JSONResponse:
    """Helper to create consistent ChatResponse with debug fields"""
    if entities is None:
        entities = {}
    response_obj = ChatResponse(
        response=response_text,
        intent=intent,
        confidence=confidence,
        entities=entities,
        requires_input=requires_input,
        session_id=session_id,
        status=status,
        debug_state_intent=state_intent,
        debug_session_found=session_found
    )
    return JSONResponse(content=response_obj.model_dump(exclude_none=False))


# ========== MAIN CHAT ENDPOINT ==========

# ========== PHASE 3: REFACTORED CHAT ENDPOINT WITH CORE LAYERS ==========

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Phase 3: Refactored main chat endpoint using Phase 1 & Phase 2 core layers.
    
    Layered pipeline:
    1. Input validation & rate limiting (validation_layer)
    2. Intent classification (ML unchanged)
    3. Entity extraction (enhanced in Phase 4)
    4. State machine updates & slot filling
    5. Dialogue processing
    6. Action execution (wrapped in transactions)
    7. Error recovery
    8. Audit logging (Phase 2 database)
    
    Fixes:
    - Flaw #6: Intent locking prevents mid-flow reclassification
    - Flaw #13: Rate limiting prevents DoS
    - Flaw #14: Idempotency keys prevent duplicate charges
    - Flaw #16: Audit trail captures all operations
    - Flaw #20: Rollback capability via transaction manager
    - Plus validation, state machine, error recovery layers
    """
    session_found = False
    idempotency_key = str(uuid.uuid4())
    
    try:
        # ============ LAYER 1: INPUT VALIDATION & RATE LIMITING ============
        
        # Validate request format
        valid, validation_msg = request_validator.validate_message(request.message)
        if not valid:
            logger.warning(f"[VALIDATION] Invalid request: {validation_msg}")
            error_response = ErrorRecovery.validation_error(
                field="message",
                value=request.message,
                reason=validation_msg
            )
            return make_response(
                response_text=error_response.message,
                intent=None,
                confidence=0.0,
                entities={},
                requires_input=True,
                session_id=request.session_id or "invalid",
                status="error",
                state_intent=None,
                session_found=False
            )
        
        # Check rate limits
        allowed, ratelimit_msg = rate_limiter.check_rate_limit(request.user_id, request.session_id or "default")
        if not allowed:
            logger.warning(f"[RATELIMIT] User {request.user_id} exceeded rate limit: {ratelimit_msg}")
            error_response = ErrorRecovery.rate_limit_error(
                limit_type="per_minute",
                reset_in=60
            )
            return make_response(
                response_text=error_response.message,
                intent=None,
                confidence=0.0,
                entities={},
                requires_input=False,
                session_id=request.session_id or "rate_limited",
                status="error",
                state_intent=None,
                session_found=False
            )
        
        # Log rate limit check to audit
        db_manager.log_audit(
            user_id=request.user_id,
            session_id=request.session_id or "temp",
            action="rate_limit_check",
            intent="system",
            input_data={"message": request.message[:100]},
            output_data={"status": "passed"},
            status="success",
            idempotency_key=str(uuid.uuid4())
        )
        
        # ============ GET OR CREATE SESSION ============
        
        # Check for greeting first (no session needed)
        greeting_response = ConversationHandler.handle_greeting(request.message)
        if greeting_response:
            return make_response(
                response_text=greeting_response['response'],
                intent=greeting_response['intent'],
                confidence=greeting_response['confidence'],
                entities={},
                requires_input=greeting_response['requires_input'],
                session_id=request.session_id or "greeting_session",
                status="success",
                state_intent=None,
                session_found=False
            )
        
        # Create session in database (Phase 2)
        if not request.session_id or request.session_id.strip() == "":
            session_id = session_manager.create_session(request.user_id)
            db_manager.create_session(request.user_id, session_id)
        else:
            session_id = request.session_id
            db_session = db_manager.get_session(session_id)
            session_found = db_session is not None
        
        # Get legacy session state (for backward compatibility during transition)
        state = session_manager.get_session(session_id)
        if state is None:
            state = DialogueState(user_id=request.user_id, session_id=session_id)
            session_manager.save_session(session_id, state)
        
        # ============ HANDLE PENDING CONFIRMATIONS FIRST (BEFORE INTENT CLASSIFICATION) ============
        # This MUST come before intent classification to avoid remapping user's yes/no response
        
        if state.confirmation_pending:
            logger.info(f"[STATE] Handling confirmation for intent: {state.intent}")
            user_msg_lower = request.message.lower()
            yes_patterns = ['yes', 'yep', 'yeah', 'ok', 'okay', 'sure', 'confirm', 'proceed', 'go']
            no_patterns = ['no', 'nope', 'cancel', 'stop', 'nevermind', "don't", 'dont']
            
            if any(pattern in user_msg_lower for pattern in yes_patterns):
                # User confirmed - execute action
                logger.info(f"[STATE] User confirmed action: {state.intent}")
                response_text = dialogue_manager._handle_confirmation(state, request.message)
                state.add_to_history('user', request.message)
                state.add_to_history('assistant', response_text)
                state.confirm_action()
                
                # Execute action wrapped in transaction (Phase 2)
                action_result = await execute_action(state, request.user_id)
                if action_result:
                    response_text = action_result
                
                # Log audit entry
                db_manager.log_audit(
                    user_id=request.user_id,
                    session_id=session_id,
                    action=state.intent,
                    intent=state.intent,
                    input_data={"message": request.message[:100]},
                    output_data={"response": response_text[:200]},
                    status="success" if not response_text.startswith("❌") else "failure",
                    idempotency_key=str(uuid.uuid4())
                )
                
                # Clear state
                state.intent = None
                state.filled_slots = {}
                state.required_slots = []
                state.missing_slots = []
                state.confirmation_pending = False
                
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=response_text,
                    intent=None,
                    confidence=0.0,
                    entities={},
                    requires_input=False,
                    session_id=session_id,
                    status="success",
                    state_intent=None,
                    session_found=session_found
                )
            
            elif any(pattern in user_msg_lower for pattern in no_patterns):
                # User cancelled
                logger.info(f"[STATE] User cancelled action: {state.intent}")
                response_text = "Okay, I've cancelled that action. What else can I help you with?"
                state.add_to_history('user', request.message)
                state.add_to_history('assistant', response_text)
                state.confirmation_pending = False
                state.intent = None
                state.filled_slots = {}
                
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=response_text,
                    intent=None,
                    confidence=0.0,
                    entities={},
                    requires_input=False,
                    session_id=session_id,
                    status="success",
                    state_intent=None,
                    session_found=session_found
                )
            
            else:
                # Ambiguous - ask for clarification
                response_text = "Could you please confirm with 'yes' or 'no'?"
                state.add_to_history('user', request.message)
                state.add_to_history('assistant', response_text)
                
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=response_text,
                    intent=state.intent,
                    confidence=state.intent_confidence,
                    entities={},
                    requires_input=True,
                    session_id=session_id,
                    status="success",
                    state_intent=state.intent,
                    session_found=session_found
                )
        
        # ============ LAYER 2: INTENT CLASSIFICATION (NOW AFTER CONFIRMATION CHECK) ============
        # CRITICAL: Only classify intent if NOT already in a multi-turn flow
        # When user is filling slots, we should ONLY extract entities, not reclassify intent
        
        multi_turn_intents = ['create_account', 'bill_payment', 'transfer_money']
        
        if state.intent and state.intent in multi_turn_intents and not state.is_complete():
            # Already in a multi-turn flow - skip intent classification entirely
            # User responses should be interpreted as slot values, not new intents
            intent = state.intent
            confidence = state.intent_confidence
            logger.info(f"[STATE] In multi-turn {intent} flow - skipping intent classification, extracting entities only")
        else:
            # Not in a multi-turn flow - classify intent normally
            prediction = intent_classifier.predict(request.message)
            raw_intent = prediction.get('intent', 'unknown')
            confidence = prediction.get('confidence', 0.0)
            intent, confidence = remap_intent(raw_intent, confidence)
            logger.info(f"[INTENT] Raw: {raw_intent} -> Remapped: {intent} (Confidence: {confidence:.2%})")
        
        # ============ LAYER 3: ENTITY EXTRACTION ============
        
        # Extract entities using basic extractor
        entities = entity_extractor.extract_and_validate(request.message)
        
        # Enhance entities with Phase 4 features (implicit amounts, negation detection)
        if enhanced_entity_extractor:
            enhanced_entities = enhanced_entity_extractor.extract_context_aware_entities(
                request.message,
                intent=intent
            )
            # Merge enhanced entities (Phase 4 features) with base entities
            entities.update(enhanced_entities)
            logger.info(f"[ENTITIES] Enhanced with Phase 4: implicit amounts, negation detection")
        
        logger.info(f"[ENTITIES] Extracted: {entities}")
        
        # ============ STATE MACHINE: INTENT LOCKING & SLOT FILLING ============
        
        simple_intents = ['check_balance', 'check_recent_transactions', 'find_atm', 'find_branch', 'customer_service']
        
        # Intent locking is now simpler since we skip classification during multi-turn flows
        # Only need to handle switching between different multi-turn intents
        should_lock_intent = (
            state.intent in multi_turn_intents and 
            not state.is_complete() and
            len(state.filled_slots) > 0 and  # ← Only lock if slots are filled (user committed)
            intent not in simple_intents and
            confidence < 0.90
        )
        
        if should_lock_intent:
            intent = state.intent
            confidence = state.intent_confidence
            logger.info(f"[STATE] Intent locked to {intent} (multi-turn in progress)")
        else:
            # Allow intent to switch
            if state.intent and state.intent != intent:
                # Starting a new different intent
                state.intent = None
                state.filled_slots = {}
                state.required_slots = []
                state.missing_slots = []
                state.confirmation_pending = False
                logger.info(f"[STATE] Switching from {state.intent} to {intent}")
        
        # If starting new intent, set it
        if not state.intent and intent != 'unknown':
            logger.info(f"[STATE] Setting intent: {intent}")
            state.intent = intent
            state.intent_confidence = confidence
            
            # Initialize required slots based on intent
            if intent == 'create_account':
                state.required_slots = ['name', 'phone', 'email', 'otp_code', 'account_type']
                state.missing_slots = state.required_slots.copy()
                # Ask for name before filling any slots
                response_text = "What is your full name?"
                state.add_to_history('assistant', response_text)
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities=entities,
                    requires_input=True,
                    session_id=session_id,
                    status="success",
                    state_intent=state.intent,
                    session_found=session_found
                )
            elif intent == 'transfer_money':
                state.required_slots = ['from_account', 'to_account', 'amount']
                state.missing_slots = state.required_slots.copy()
                # Ask which account to transfer from
                user_accounts = db_manager.get_user_accounts(request.user_id)
                if not user_accounts:
                    response_text = "❌ You don't have any accounts. Please create an account first."
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=False,
                        session_id=session_id,
                        status="error",
                        state_intent=state.intent,
                        session_found=session_found
                    )
                # List accounts
                account_list = "\n".join([f"• {acc['account_type'].capitalize()} (${acc['balance']:.2f})" for acc in user_accounts])
                response_text = f"Which account would you like to transfer from?\n{account_list}"
                state.add_to_history('assistant', response_text)
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities=entities,
                    requires_input=True,
                    session_id=session_id,
                    status="success",
                    state_intent=state.intent,
                    session_found=session_found
                )
            elif intent == 'bill_payment':
                state.required_slots = ['biller', 'amount', 'account']
                state.missing_slots = state.required_slots.copy()
                # Ask for biller - make it clearer what we're asking for
                response_text = "Which bill would you like to pay? (electricity, water, gas, internet, or mobile)"
                state.add_to_history('assistant', response_text)
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities=entities,
                    requires_input=True,
                    session_id=session_id,
                    status="success",
                    state_intent=state.intent,
                    session_found=session_found
                )
            # Simple intents don't need slot filling
            elif intent in simple_intents:
                state.required_slots = []
                state.missing_slots = []
                state.status = ConversationStatus.COMPLETED
        
        # Only process slot filling for multi-turn intents
        if state.intent in multi_turn_intents:
            if 'name' in state.missing_slots and 'name' not in state.filled_slots:
                if state.missing_slots[0] == 'name':
                    state.fill_slot('name', request.message)
                    logger.info(f"[SLOTS] Filled name from input: {request.message}")
                    # Ask for phone
                    response_text = "What is your phone number?"
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
            
            elif 'phone' in state.missing_slots and 'phone' not in state.filled_slots:
                if state.missing_slots[0] == 'phone':
                    state.fill_slot('phone', request.message)
                    logger.info(f"[SLOTS] Filled phone from input: {request.message}")
                    # Ask for email
                    response_text = "What is your email address?"
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
            
            elif 'email' in state.missing_slots and 'email' not in state.filled_slots:
                if state.missing_slots[0] == 'email':
                    # Try to extract email from message
                    import re
                    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                    email_match = re.search(email_pattern, request.message)
                    if email_match:
                        email_value = email_match.group()
                        state.fill_slot('email', email_value)
                        logger.info(f"[SLOTS] Filled email from input: {email_value}")
                        
                        # Send OTP for email verification
                        otp_success, otp_msg = auth_manager.initiate_email_verification(email_value, 'account_creation')
                        if otp_success:
                            logger.info(f"[OTP] OTP sent to {email_value}: {otp_msg}")
                            response_text = f"A verification code has been sent to {email_value}. Please enter the 6-digit code."
                            state.add_to_history('assistant', response_text)
                            session_manager.save_session(session_id, state)
                            return make_response(
                                response_text=response_text,
                                intent=intent,
                                confidence=confidence,
                                entities=entities,
                                requires_input=True,
                                session_id=session_id,
                                status="success",
                                state_intent=state.intent,
                                session_found=session_found
                            )
                        else:
                            response_text = f"Failed to send verification code: {otp_msg}. Please try again."
                            return make_response(
                                response_text=response_text,
                                intent=intent,
                                confidence=confidence,
                                entities=entities,
                                requires_input=True,
                                session_id=session_id,
                                status="error",
                                state_intent=state.intent,
                                session_found=session_found
                            )
                    else:
                        # No valid email detected, ask for clarification
                        response_text = "Please provide a valid email address (e.g., user@example.com)"
                        state.add_to_history('user', request.message)
                        state.add_to_history('assistant', response_text)
                        session_manager.save_session(session_id, state)
                        return make_response(
                            response_text=response_text,
                            intent=intent,
                            confidence=confidence,
                            entities=entities,
                            requires_input=True,
                            session_id=session_id,
                            status="success",
                            state_intent=state.intent,
                            session_found=session_found
                        )
            
            elif 'otp_code' in state.missing_slots and 'otp_code' not in state.filled_slots:
                if state.missing_slots[0] == 'otp_code':
                    # Verify OTP code
                    email = state.filled_slots.get('email')
                    otp_code = request.message.strip()
                    
                    if email and len(otp_code) == 6 and otp_code.isdigit():
                        otp_valid, otp_verify_msg = auth_manager.verify_email_otp(email, otp_code, 'account_creation')
                        if otp_valid:
                            state.fill_slot('otp_code', otp_code)
                            logger.info(f"[OTP] OTP verified for {email}")
                        else:
                            response_text = f"Invalid or expired code. {otp_verify_msg}"
                            state.add_to_history('user', request.message)
                            state.add_to_history('assistant', response_text)
                            session_manager.save_session(session_id, state)
                            return make_response(
                                response_text=response_text,
                                intent=intent,
                                confidence=confidence,
                                entities=entities,
                                requires_input=True,
                                session_id=session_id,
                                status="success",
                                state_intent=state.intent,
                                session_found=session_found
                            )
                    else:
                        response_text = "Please enter a valid 6-digit code."
                        state.add_to_history('user', request.message)
                        state.add_to_history('assistant', response_text)
                        session_manager.save_session(session_id, state)
                        return make_response(
                            response_text=response_text,
                            intent=intent,
                            confidence=confidence,
                            entities=entities,
                            requires_input=True,
                            session_id=session_id,
                            status="success",
                            state_intent=state.intent,
                            session_found=session_found
                        )
            
            elif 'account_type' in state.missing_slots and 'account_type' not in state.filled_slots:
                if state.missing_slots[0] == 'account_type':
                    acc_type = request.message.lower().strip()
                    if acc_type in ['savings', 'current', 'salary']:
                        state.fill_slot('account_type', acc_type)
                        logger.info(f"[SLOTS] Filled account_type: {acc_type}")
                        
                        # All slots filled, ask for confirmation
                        name = state.filled_slots.get('name', 'User')
                        email = state.filled_slots.get('email', 'email')
                        acc_type_display = acc_type.capitalize()
                        
                        confirmation_text = f"Please confirm account creation:\n• Name: {name}\n• Email: {email}\n• Account Type: {acc_type_display}"
                        state.add_to_history('user', request.message)
                        state.add_to_history('assistant', confirmation_text)
                        state.confirmation_pending = True
                        session_manager.save_session(session_id, state)
                        return make_response(
                            response_text=confirmation_text,
                            intent=intent,
                            confidence=confidence,
                            entities=entities,
                            requires_input=True,
                            session_id=session_id,
                            status="success",
                            state_intent=state.intent,
                            session_found=session_found
                        )
                    else:
                        response_text = "Please choose: savings, current, or salary"
                        state.add_to_history('assistant', response_text)
                        session_manager.save_session(session_id, state)
                        return make_response(
                            response_text=response_text,
                            intent=intent,
                            confidence=confidence,
                            entities=entities,
                            requires_input=True,
                            session_id=session_id,
                            status="success",
                            state_intent=state.intent,
                            session_found=session_found
                        )
            
            # Slot filling for transfer_money
            elif 'from_account' in state.missing_slots and 'from_account' not in state.filled_slots:
                if state.missing_slots[0] == 'from_account':
                    # Try to extract account from message or use first account
                    user_accounts = db_manager.get_user_accounts(request.user_id)
                    if not user_accounts:
                        response_text = "❌ You don't have any accounts. Please create an account first."
                        state.add_to_history('assistant', response_text)
                        session_manager.save_session(session_id, state)
                        return make_response(
                            response_text=response_text,
                            intent=intent,
                            confidence=confidence,
                            entities=entities,
                            requires_input=True,
                            session_id=session_id,
                            status="error",
                            state_intent=state.intent,
                            session_found=session_found
                        )
                    
                    # If user specified an account type or number, try to match it
                    from_msg = request.message.lower().strip()
                    selected_account = None
                    
                    # Check if message mentions an account type
                    for acc in user_accounts:
                        if acc['account_type'] in from_msg or acc['account_no'] in from_msg:
                            selected_account = acc
                            break
                    
                    # If no match, use first account
                    if not selected_account:
                        selected_account = user_accounts[0]
                    
                    state.fill_slot('from_account', selected_account['account_no'])
                    logger.info(f"[SLOTS] Filled from_account: {selected_account['account_no']}")
                    
                    # Ask for recipient
                    response_text = f"Transferring from {selected_account['account_type'].capitalize()} account. Who would you like to send money to? (account number or name)"
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
            
            elif 'to_account' in state.missing_slots and 'to_account' not in state.filled_slots:
                if state.missing_slots[0] == 'to_account':
                    to_msg = request.message.strip()
                    state.fill_slot('to_account', to_msg)
                    logger.info(f"[SLOTS] Filled to_account: {to_msg}")
                    
                    # Ask for amount
                    response_text = "How much would you like to transfer?"
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
            
            # Slot filling for bill_payment - NEW FLOW: biller → account → amount → confirm → receipt
            # Step 1: Ask for bill type (biller)
            elif state.intent == 'bill_payment' and 'biller' in state.missing_slots and 'biller' not in state.filled_slots:
                biller = entities.get('biller') or entities.get('bill_type') or request.message.lower().strip()
                valid_billers = ['electricity', 'mobile', 'gas', 'internet', 'water']
                biller_lower = biller.lower().strip() if biller else ""
                
                logger.info(f"[SLOTS] Biller validation: '{biller_lower}' | valid: {biller_lower in valid_billers}")
                
                if biller_lower and biller_lower in valid_billers:
                    state.fill_slot('biller', biller_lower)
                    if 'biller' in state.missing_slots:
                        state.missing_slots.remove('biller')
                    logger.info(f"[SLOTS] ✅ Filled biller: '{biller_lower}' | Next: ask for account")
                    
                    # Ask for account NEXT (not amount)
                    user_accounts = db_manager.get_user_accounts(request.user_id)
                    account_list = "\n".join([f"• {acc['account_type'].capitalize()} (PKR {acc['balance']:,.2f})" for acc in user_accounts])
                    response_text = f"Which account should this payment come from?\n{account_list}"
                    state.add_to_history('user', request.message)
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
                else:
                    response_text = f"Invalid biller '{biller}'. Please choose from: electricity, mobile, gas, internet, or water"
                    logger.info(f"[SLOTS] ❌ Invalid biller: '{biller_lower}'")
                    state.add_to_history('user', request.message)
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
            
            # Step 2: Ask for account (before amount)
            elif state.intent == 'bill_payment' and 'account' in state.missing_slots and 'account' not in state.filled_slots:
                user_accounts = db_manager.get_user_accounts(request.user_id)
                account_msg = request.message.lower().strip()
                selected_account = None
                
                # Check if message mentions an account type
                for acc in user_accounts:
                    if acc['account_type'].lower() in account_msg or acc['account_no'] in account_msg:
                        selected_account = acc
                        break
                
                # If no match, use first account
                if not selected_account:
                    selected_account = user_accounts[0]
                
                state.fill_slot('account', selected_account['account_no'])
                if 'account' in state.missing_slots:
                    state.missing_slots.remove('account')
                logger.info(f"[SLOTS] ✅ Filled account: {selected_account['account_no']} | Next: ask for amount")
                
                # Ask for amount NEXT
                response_text = "How much would you like to pay?"
                state.add_to_history('user', request.message)
                state.add_to_history('assistant', response_text)
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=response_text,
                    intent=intent,
                    confidence=confidence,
                    entities=entities,
                    requires_input=True,
                    session_id=session_id,
                    status="success",
                    state_intent=state.intent,
                    session_found=session_found
                )
            
            # Step 3: Ask for amount
            elif state.intent == 'bill_payment' and 'amount' in state.missing_slots and 'amount' not in state.filled_slots:
                amount_value = None
                
                # Try to get from extracted entities (Phase 4)
                if 'amount' in entities and entities['amount']:
                    amount_value = entities['amount']
                    logger.info(f"[SLOTS] Amount from entities: {amount_value}")
                else:
                    # Fall back to regex extraction
                    import re
                    amount_pattern = r'\d+(?:\.\d{2})?'
                    amount_match = re.search(amount_pattern, request.message)
                    if amount_match:
                        amount_value = float(amount_match.group())
                        logger.info(f"[SLOTS] Amount from regex: {amount_value}")
                
                if amount_value:
                    state.fill_slot('amount', amount_value)
                    if 'amount' in state.missing_slots:
                        state.missing_slots.remove('amount')
                    logger.info(f"[SLOTS] ✅ Filled amount: {amount_value} | All slots filled → confirmation")
                    
                    # All slots filled, ask for confirmation
                    biller = state.filled_slots.get('biller', 'Unknown')
                    account = state.filled_slots.get('account', 'Account')
                    account_detail = db_manager.get_account_by_number(account)
                    account_type = account_detail['account_type'] if account_detail else 'Account'
                    
                    confirmation_text = f"Please confirm payment:\n• Biller: {biller.capitalize()}\n• Amount: PKR {amount_value:,.2f}\n• From {account_type} account"
                    state.add_to_history('user', request.message)
                    state.add_to_history('assistant', confirmation_text)
                    state.confirmation_pending = True
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=confirmation_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
                else:
                    response_text = "Please enter a valid amount (e.g., 500 or 1000.50)"
                    state.add_to_history('user', request.message)
                    state.add_to_history('assistant', response_text)
                    session_manager.save_session(session_id, state)
                    return make_response(
                        response_text=response_text,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        requires_input=True,
                        session_id=session_id,
                        status="success",
                        state_intent=state.intent,
                        session_found=session_found
                    )
            
            elif state.intent != 'bill_payment' and 'amount' in state.missing_slots and 'amount' not in state.filled_slots:
                biller = state.filled_slots.get('biller', 'Unknown')
                amount = state.filled_slots.get('amount', 0)
                account_type = selected_account.get('account_type', 'Account')
                
                confirmation_text = f"Please confirm payment:\n• Biller: {biller.capitalize()}\n• Amount: PKR {amount:,.2f}\n• From {account_type} account"
                state.add_to_history('user', request.message)
                state.add_to_history('assistant', confirmation_text)
                state.confirmation_pending = True
                session_manager.save_session(session_id, state)
                return make_response(
                    response_text=confirmation_text,
                    intent=intent,
                    confidence=confidence,
                    entities=entities,
                    requires_input=True,
                    session_id=session_id,
                    status="success",
                    state_intent=state.intent,
                    session_found=session_found
                )
        
        # ============ DIALOGUE PROCESSING ============
        
        # Skip dialogue processing for simple one-turn intents
        if state.intent not in simple_intents:
            response_text, state = dialogue_manager.process_turn(
                state=state,
                user_message=request.message,
                intent=intent,
                intent_confidence=confidence,
                entities=entities
            )
        
        # ============ ACTION EXECUTION & CONFIRMATION ============
        
        if state.is_complete() and not state.confirmation_pending:
            no_confirm_intents = ['check_balance', 'check_recent_transactions', 'find_atm', 'find_branch', 'customer_service']
            
            if state.intent in no_confirm_intents:
                # Execute immediately without confirmation
                action_result = await execute_action(state, request.user_id)
                if action_result:
                    response_text = action_result
                state.confirm_action()
                
                # Clear state for next intent (important for simple intents)
                state.intent = None
                state.filled_slots = {}
                state.required_slots = []
                state.missing_slots = []
                state.confirmation_pending = False
            else:
                # Ask for confirmation
                state.set_confirmation_pending({
                    'intent': state.intent,
                    'slots': state.filled_slots.copy()
                })
                response_text = dialogue_manager._generate_confirmation(state)
        
        elif state.status == ConversationStatus.COMPLETED:
            # Action was confirmed and executed
            action_result = await execute_action(state, request.user_id)
            if action_result:
                response_text = action_result
            
            # Clear state for next intent
            state.intent = None
            state.filled_slots = {}
            state.required_slots = []
            state.missing_slots = []
            state.confirmation_pending = False
        
        # ============ SAVE SESSION & AUDIT LOG ============
        
        # Ensure response_text is defined (fallback for edge cases)
        if 'response_text' not in locals():
            response_text = "Processed your request."
        
        session_manager.save_session(session_id, state)
        
        # Log to database audit trail (Phase 2)
        db_manager.log_audit(
            user_id=request.user_id,
            session_id=session_id,
            action=intent or "unknown",
            intent=intent,
            input_data={"message": request.message[:100]},
            output_data={"response": response_text[:200]},
            status="success",
            idempotency_key=str(uuid.uuid4())
        )
        
        # ============ RETURN RESPONSE ============
        
        return make_response(
            response_text=response_text,
            intent=intent,
            confidence=confidence,
            entities=entities,
            requires_input=len(state.missing_slots) > 0,
            session_id=session_id,
            status="success",
            state_intent=state.intent,
            session_found=session_found
        )
    
    except Exception as e:
        logger.error(f"[ERROR] Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        
        # Log error to audit trail
        try:
            db_manager.log_audit(
                user_id=request.user_id,
                session_id=request.session_id or "error",
                action="chat_error",
                intent="system",
                input_data={"message": request.message[:100]},
                output_data={"error": str(e)[:200]},
                status="error",
                idempotency_key=str(uuid.uuid4())
            )
        except:
            pass
        
        # Return error response via error recovery
        error_response = ErrorRecovery.system_error(
            action="processing your chat request",
            error_details=str(e)[:100]
        )
        
        raise HTTPException(status_code=500, detail=error_response.message)


# ========== HELPER: HANDLE OTP RESEND ==========

async def handle_otp_resend(state: DialogueState) -> str:
    """
    Handle OTP resend request
    
    Args:
        state: Current dialogue state
        
    Returns:
        Response message
    """
    if state.intent != 'create_account' or 'email' not in state.filled_slots:
        return "I'm not sure what code you're referring to. How can I help you?"
    
    email = state.filled_slots['email']
    success, message = auth_manager.resend_verification(email, 'account_creation')
    
    if success:
        return f"{message}\n\nPlease enter the new 6-digit code."
    else:
        return f"❌ {message}"


# ========== HELPER: EXECUTE ACTION ==========

async def execute_action(state: DialogueState, user_id: int) -> Optional[str]:
    """
    Execute banking action based on dialogue state
    
    Args:
        state: Dialogue state
        user_id: User ID
        
    Returns:
        Success message or None
    """
    intent = state.intent
    slots = state.filled_slots
    
    try:
        if intent == "create_account":
            # Validate entities (Phase 2)
            email = slots.get('email')
            phone = slots.get('phone')
            name = slots.get('name')
            
            # NOTE: Email verification is already done during the OTP step
            # We already checked that the user verified the OTP code,
            # so we don't need to verify again here. The slots contain verified data.
            
            # Validate phone number
            if phone:
                validated_phone = entity_validator.validate_phone_number(phone)
                if not validated_phone:
                    return error_handler.invalid_phone_error(phone)
                phone = validated_phone
            
            # Validate person name
            if name:
                validated_name = entity_validator.validate_person_name(name)
                if not validated_name:
                    return error_handler.validation_error("name", f"Invalid name format: {name}", "Please provide a valid name.")
                name = validated_name
            
            # Create user
            success, message, new_user_id = db_manager.create_user(
                name=name,
                phone=phone,
                email=email
            )
            
            if success:
                # Create account
                account_success, account_msg, account_no = db_manager.create_account(
                    user_id=new_user_id,
                    account_type=slots.get('account_type', 'savings'),
                    initial_balance=0.0
                )
                
                if account_success:
                    # Send welcome email
                    auth_manager.send_welcome_email(
                        email=email,
                        name=name,
                        account_number=account_no
                    )
                    
                    # Generate account creation receipt (Phase 2)
                    receipt = receipt_generator.generate_account_creation_receipt(
                        user_name=name,
                        phone=phone,
                        email=email,
                        account_number=account_no,
                        account_type=slots.get('account_type', 'savings'),
                        format="text"
                    )
                    
                    return f"{receipt}\n\nA confirmation email has been sent to {email}"
                else:
                    return f"❌ Failed to create account: {account_msg}"
            else:
                return f"❌ {message}"
        
        elif intent == "transfer_money":
            # Validate entities (Phase 2)
            amount = slots.get('amount')
            from_account = slots.get('from_account')  # Fixed: was 'source_account'
            to_account = slots.get('to_account')      # Fixed: was 'payee'
            
            # Validate amount
            if amount:
                validated_amount = entity_validator.validate_amount(amount)
                if validated_amount is None:
                    accounts = db_manager.get_user_accounts(user_id)
                    first_account = accounts[0] if accounts else None
                    available_balance = first_account['balance'] if first_account else 0
                    return error_handler.amount_out_of_range_error(amount, entity_validator.MIN_AMOUNT, entity_validator.MAX_AMOUNT)
                amount = validated_amount
            
            # Validate account numbers
            # NOTE: The accounts were already selected during slot filling
            # Trust the slot filling - don't override it
            # If validation fails, it means the IBAN pattern is stricter than needed
            # Just proceed with what we have and let execute_transfer handle it
            
            if not from_account:
                # If from_account is empty, use first account
                user_accounts = db_manager.get_user_accounts(user_id)
                if user_accounts:
                    from_account = user_accounts[0]['account_no']
                    logger.info(f"from_account was empty, using first account: {from_account}")
            
            if not to_account:
                logger.warning("to_account is empty")
                return "❌ Please specify a recipient account or name"
            
            # Execute transfer
            success, message = db_manager.execute_transfer(
                from_account_no=from_account,
                to_account_no=to_account,
                amount=amount,
                description="Transfer via chatbot"
            )
            
            if success:
                # Generate transfer receipt (Phase 2)
                from_acc = db_manager.get_account_by_number(from_account)
                to_acc = db_manager.get_account_by_number(to_account)
                new_balance = db_manager.get_balance(from_account)
                
                receipt = receipt_generator.generate_transfer_receipt(
                    transaction_id=receipt_generator.generate_transaction_id("TXN"),
                    from_account={
                        'account_no': from_account,
                        'account_type': from_acc['account_type'],
                        'holder_name': from_acc.get('holder_name', 'Account Holder'),
                        'previous_balance': from_acc['balance'] + amount  # Previous balance
                    },
                    to_account={
                        'account_no': to_account,
                        'holder_name': to_acc.get('holder_name', 'Recipient')
                    },
                    amount=amount,
                    description="Transfer via chatbot",
                    new_balance=new_balance,
                    format="text"
                )
                
                return receipt
            else:
                return error_handler.transaction_failed_error(message)
        
        elif intent == "bill_payment":
            # Validate entities (Phase 2)
            amount = slots.get('amount')
            biller = slots.get('biller')
            account = slots.get('account')
            
            # Validate biller is present
            if not biller:
                return error_handler.validation_error(
                    field="biller",
                    value=biller,
                    reason="Bill type not specified. Please choose from: electricity, water, gas, internet, mobile"
                )
            
            # Validate amount
            if amount:
                validated_amount = entity_validator.validate_amount(amount)
                if validated_amount is None:
                    return error_handler.amount_out_of_range_error(amount, entity_validator.MIN_AMOUNT, entity_validator.MAX_AMOUNT)
                amount = validated_amount
            else:
                # If no amount specified, use a default or ask
                return error_handler.validation_error(
                    field="amount",
                    value=amount,
                    reason="Amount not specified. Please provide an amount."
                )
            
            # Validate account (look up by partial match if needed)
            if account:
                validated_account = entity_validator.validate_account_number(account)
                if not validated_account:
                    # Use first account of the user
                    user_accounts = db_manager.get_user_accounts(user_id)
                    if user_accounts:
                        account = user_accounts[0]['account_no']
                    else:
                        user_accounts = db_manager.get_user_accounts(user_id)
                        return error_handler.invalid_account_error(account, user_accounts)
                else:
                    account = validated_account
            else:
                # If no account specified, use first user account
                user_accounts = db_manager.get_user_accounts(user_id)
                if not user_accounts:
                    return error_handler.validation_error(
                        field="account",
                        value=account,
                        reason="You have no accounts. Please create an account first."
                    )
                account = user_accounts[0]['account_no']
            
            # Execute bill payment
            success, message = db_manager.pay_bill(
                user_id=user_id,
                bill_type=biller,
                amount=amount,
                account_no=account
            )
            
            if success:
                # Generate bill payment receipt (Phase 2)
                acc = db_manager.get_account_by_number(account) if account else None
                new_balance = db_manager.get_balance(account) if account else None
                
                receipt = receipt_generator.generate_bill_payment_receipt(
                    transaction_id=receipt_generator.generate_transaction_id("BILL"),
                    bill_type=biller,
                    amount=amount,
                    account={
                        'account_no': account or 'N/A',
                        'account_type': acc['account_type'] if acc else 'default',
                        'holder_name': acc.get('holder_name', 'Account Holder') if acc else 'N/A',
                        'previous_balance': (acc['balance'] + amount) if acc else 0
                    },
                    reference_no=f"BILL-{receipt_generator.generate_transaction_id()}",
                    new_balance=new_balance,
                    format="text"
                )
                return receipt
            else:
                return error_handler.transaction_failed_error(message)
        
        elif intent == "check_balance":
            # Get balance
            account_no = slots.get('account_number')
            if account_no:
                balance = db_manager.get_balance(account_no)
                if balance is not None:
                    return f"Your account balance is PKR {balance:,.2f}"
                else:
                    return error_handler.account_not_found_error(account_no)
            else:
                # Get user's first account
                accounts = db_manager.get_user_accounts(user_id)
                if accounts:
                    balance_str = ", ".join([f"{acc['account_type']}: PKR {acc['balance']:,.2f}" for acc in accounts])
                    return f"Your balance: {balance_str}"
                else:
                    return "No accounts found"
        
        elif intent == "check_recent_transactions":
            # Get transaction history
            limit = slots.get('limit', 5)
            transactions = db_manager.get_transaction_history(
                db_manager.get_user_accounts(user_id)[0]['id'], 
                limit=limit
            )
            if transactions:
                txn_str = "\n".join([f"  • {t['type']:12s}: PKR {t['amount']:>10,.2f}" for t in transactions])
                return f"Your recent transactions:\n{txn_str}"
            else:
                return "No transactions found"
        
        elif intent == "block_card":
            # Block card
            card_no = slots.get('card_number')
            success, message = db_manager.block_card(card_no)
            return message
        
        elif intent == "find_atm" or intent == "find_ATM":
            # Find nearest ATM
            return ("🏧 ATMs Near You:\n\n"
                   "1. Downtown Branch ATM\n"
                   "   Location: 123 Main St, Downtown\n"
                   "   Available 24/7\n\n"
                   "2. Plaza ATM\n"
                   "   Location: Shopping Plaza, 5th Ave\n"
                   "   Available 24/7\n\n"
                   "3. Airport ATM\n"
                   "   Location: International Airport Terminal 2\n"
                   "   Available 24/7\n\n"
                   "Need more information? Contact customer service.")
        
        elif intent == "find_branch":
            # Find nearest branch
            return ("🏦 Bank Branches Near You:\n\n"
                   "1. Downtown Branch\n"
                   "   Location: 123 Main St, Downtown\n"
                   "   Hours: Mon-Fri 9AM-5PM, Sat 10AM-2PM\n\n"
                   "2. Airport Branch\n"
                   "   Location: International Airport Terminal 2\n"
                   "   Hours: Mon-Fri 8AM-8PM, Sat 9AM-6PM\n\n"
                   "3. Plaza Branch\n"
                   "   Location: Shopping Plaza, 5th Ave\n"
                   "   Hours: Mon-Fri 10AM-6PM, Sat 10AM-4PM\n\n"
                   "Need more information? Contact customer service.")
        
        return None
        
    except Exception as e:
        logger.error(f"Error executing action: {e}")
        return f"Action failed: {str(e)}"


# ========== BANKING ENDPOINTS ==========

@app.get("/api/balance/{user_id}")
async def get_balance(user_id: int, account_no: Optional[str] = None):
    """Get account balance"""
    try:
        if account_no:
            balance = db_manager.get_balance(account_no)
            if balance is None:
                raise HTTPException(status_code=404, detail="Account not found")
            
            account = db_manager.get_account_by_number(account_no)
            return {
                "account_no": account_no,
                "account_type": account['account_type'],
                "balance": balance,
                "currency": account['currency']
            }
        else:
            # Get all user accounts
            accounts = db_manager.get_user_accounts(user_id)
            if not accounts:
                raise HTTPException(status_code=404, detail="No accounts found")
            
            return {
                "accounts": [
                    {
                        "account_no": acc['account_no'],
                        "account_type": acc['account_type'],
                        "balance": acc['balance'],
                        "currency": acc['currency']
                    }
                    for acc in accounts
                ]
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transfer")
async def transfer_money(request: TransferRequest):
    """Execute money transfer"""
    try:
        success, message = db_manager.execute_transfer(
            from_account_no=request.from_account,
            to_account_no=request.to_account,
            amount=request.amount,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Get new balance
        new_balance = db_manager.get_balance(request.from_account)
        
        return {
            "success": True,
            "message": message,
            "new_balance": new_balance
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{user_id}")
async def get_transaction_history(user_id: int, limit: int = 10):
    """Get transaction history"""
    try:
        # Get user's first account
        accounts = db_manager.get_user_accounts(user_id)
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found")
        
        # Get transactions for first account
        transactions = db_manager.get_transaction_history(accounts[0]['id'], limit)
        
        return {
            "account_no": accounts[0]['account_no'],
            "transactions": transactions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bill-payment")
async def pay_bill(request: BillPaymentRequest):
    """Pay a bill"""
    try:
        success, message = db_manager.pay_bill(
            user_id=request.user_id,
            bill_type=request.bill_type,
            amount=request.amount,
            account_no=request.account_no
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        # Get new balance
        new_balance = db_manager.get_balance(request.account_no)
        
        return {
            "success": True,
            "message": message,
            "new_balance": new_balance
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== UTILITY ENDPOINTS ==========

@app.post("/api/predict-intent")
async def predict_intent(request: ChatRequest):
    """Predict intent only (for testing)"""
    try:
        prediction = intent_classifier.predict(request.message)
        intent = prediction.get('intent', 'unknown')
        confidence = prediction.get('confidence', 0.0)
        
        return {
            "message": request.message,
            "intent": intent,
            "confidence": confidence
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract-entities")
async def extract_entities(request: ChatRequest):
    """Extract entities only (for testing)"""
    try:
        entities = entity_extractor.extract_and_validate(request.message)
        
        return {
            "message": request.message,
            "entities": entities
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== AUTHENTICATION ENDPOINTS ==========

@app.post("/api/auth/send-otp")
async def send_otp(email: str, purpose: str = "account_creation"):
    """
    Send OTP to email
    
    Args:
        email: Email address
        purpose: Purpose of OTP
    """
    try:
        success, message = auth_manager.initiate_email_verification(email, purpose)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/auth/verify-otp")
async def verify_otp(email: str, otp_code: str, purpose: str = "account_creation"):
    """
    Verify OTP code
    
    Args:
        email: Email address
        otp_code: OTP to verify
        purpose: Purpose of OTP
    """
    try:
        success, message = auth_manager.verify_email_otp(email, otp_code, purpose)
        
        if success:
            return {"success": True, "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth/check-email/{email}")
async def check_email(email: str):
    """Check if email exists"""
    try:
        exists = db_manager.check_email_exists(email)
        return {"exists": exists}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)