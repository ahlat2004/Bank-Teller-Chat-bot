"""
Error Recovery - Helpful error messages and recovery paths
Fixes Flaw: #15 (No Recovery Paths)
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


class ErrorType(Enum):
    """Error type categorization"""
    VALIDATION_ERROR = "validation_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    SYSTEM_ERROR = "system_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    AUTHENTICATION_ERROR = "authentication_error"


@dataclass
class ErrorResponse:
    """Standardized error response"""
    error_type: ErrorType
    message: str
    recovery_suggestions: List[str]
    error_details: Optional[Dict[str, Any]] = None
    support_contact: str = "support@bank.com"
    support_ticket_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "recovery_suggestions": self.recovery_suggestions,
            "error_details": self.error_details,
            "support_contact": self.support_contact,
            "support_ticket_id": self.support_ticket_id,
        }


class ErrorRecovery:
    """
    Error handling with recovery paths
    Provides helpful error messages and next steps for common banking errors
    """
    
    # Common validation patterns for banking
    VALID_EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    VALID_PHONE_PATTERN = r'^\+?1?\d{10,14}$'
    VALID_ACCOUNT_PATTERN = r'^\d{10,16}$'
    
    @staticmethod
    def validation_error(field: str, value: Any, reason: str, context: Optional[Dict] = None) -> ErrorResponse:
        """
        Handle validation errors with helpful feedback
        
        Args:
            field: Field name that failed validation
            value: Value that was invalid
            reason: Reason for validation failure
            context: Additional context about the error
        
        Returns:
            ErrorResponse with helpful message and recovery suggestions
        """
        message = f"Invalid {field}: {reason}"
        
        # Generate specific recovery suggestions based on field
        suggestions = ErrorRecovery._get_field_recovery_suggestions(field, value, context)
        
        details = {
            "field": field,
            "invalid_value": str(value),
            "reason": reason,
        }
        if context:
            details["context"] = context
        
        return ErrorResponse(
            error_type=ErrorType.VALIDATION_ERROR,
            message=message,
            recovery_suggestions=suggestions,
            error_details=details,
        )
    
    @staticmethod
    def _get_field_recovery_suggestions(field: str, value: Any, context: Optional[Dict] = None) -> List[str]:
        """Generate field-specific recovery suggestions"""
        
        field_lower = field.lower()
        
        if 'email' in field_lower:
            return [
                "Please enter a valid email address (format: user@domain.com)",
                "Check for typos in your email",
                "Use only letters, numbers, dots, and hyphens",
            ]
        elif 'phone' in field_lower:
            return [
                "Please enter a valid phone number (10-14 digits)",
                "Include country code if outside your region (+1 for US/Canada)",
                "Remove any non-digit characters except the leading +",
            ]
        elif 'amount' in field_lower:
            return [
                "Please enter a valid amount (numbers only, e.g., 5000)",
                "Amount must be positive",
                "Amount must be less than or equal to your account balance",
                f"You entered: {value}. Please try again.",
            ]
        elif 'account' in field_lower:
            available = context.get('available_accounts', []) if context else []
            suggestions = ["Please enter a valid account number (10-16 digits)"]
            if available:
                suggestions.append(f"Your accounts: {', '.join(available)}")
            suggestions.append("Check your account statement for your account number")
            return suggestions
        elif 'name' in field_lower:
            return [
                "Please enter your full name (letters only)",
                "Use your legal name as it appears on your ID",
                "Minimum 2 characters, maximum 100 characters",
            ]
        else:
            return [
                f"Please provide valid input for {field}",
                "Check the format and try again",
                "Contact support@bank.com if you need help",
            ]
    
    @staticmethod
    def insufficient_balance_error(account_type: str, available: float, requested: float) -> ErrorResponse:
        """
        Handle insufficient balance error
        Suggests alternatives
        
        Args:
            account_type: Type of account (checking, savings, etc.)
            available: Available balance
            requested: Requested amount
        
        Returns:
            ErrorResponse with alternatives
        """
        shortfall = requested - available
        
        message = (
            f"Insufficient balance in your {account_type} account. "
            f"You have PKR {available:.2f} but requested PKR {requested:.2f}. "
            f"Shortfall: PKR {shortfall:.2f}"
        )
        
        suggestions = [
            f"Reduce the amount to PKR {available:.2f} or less",
            "Transfer funds from another account first",
            "Check if you have other accounts available",
            "Consider using a credit card or overdraft facility",
            "Contact our support team for payment plan options",
        ]
        
        details = {
            "account_type": account_type,
            "available_balance": available,
            "requested_amount": requested,
            "shortfall": shortfall,
        }
        
        return ErrorResponse(
            error_type=ErrorType.BUSINESS_LOGIC_ERROR,
            message=message,
            recovery_suggestions=suggestions,
            error_details=details,
        )
    
    @staticmethod
    def account_not_found_error(account_identifier: str, available_accounts: List[Dict[str, str]]) -> ErrorResponse:
        """
        Handle account not found error
        Lists available accounts and suggests which to use
        
        Args:
            account_identifier: Account number or type that wasn't found
            available_accounts: List of user's available accounts
        
        Returns:
            ErrorResponse with available account options
        """
        message = f"Account '{account_identifier}' not found. Here are your available accounts:"
        
        account_list = []
        suggestions = []
        
        for idx, account in enumerate(available_accounts, 1):
            account_no = account.get('account_no', 'N/A')
            account_type = account.get('type', 'N/A')
            balance = account.get('balance', 0)
            
            account_list.append(f"  {idx}. {account_type} (#{account_no}) - Balance: PKR {balance:.2f}")
            suggestions.append(f"Use '{account_type}' account (#{account_no})")
        
        full_message = message + "\n" + "\n".join(account_list)
        
        details = {
            "requested_account": account_identifier,
            "available_accounts": available_accounts,
        }
        
        return ErrorResponse(
            error_type=ErrorType.BUSINESS_LOGIC_ERROR,
            message=full_message,
            recovery_suggestions=suggestions[:3],  # Top 3 suggestions
            error_details=details,
        )
    
    @staticmethod
    def duplicate_request_error() -> ErrorResponse:
        """Handle duplicate request error"""
        message = "This request was already processed. Returning previous result."
        
        suggestions = [
            "Your previous request was successful and has been returned",
            "Check your transaction history for details",
            "If you need a new transaction, please ask again",
        ]
        
        return ErrorResponse(
            error_type=ErrorType.BUSINESS_LOGIC_ERROR,
            message=message,
            recovery_suggestions=suggestions,
        )
    
    @staticmethod
    def rate_limit_error(limit_type: str, reset_in: int) -> ErrorResponse:
        """
        Handle rate limit error
        
        Args:
            limit_type: Type of limit (minute, hour, day)
            reset_in: Seconds until limit resets
        
        Returns:
            ErrorResponse explaining rate limit
        """
        time_unit = "second" if reset_in < 60 else ("minute" if reset_in < 3600 else "hour")
        time_value = (
            reset_in if reset_in < 60
            else (reset_in // 60 if reset_in < 3600 else reset_in // 3600)
        )
        
        message = (
            f"You've sent too many requests. "
            f"Please wait {time_value} {time_unit}{'s' if time_value > 1 else ''} before trying again."
        )
        
        suggestions = [
            "Take a break and try again later",
            f"You can make another request in about {time_value} {time_unit}",
            "Avoid sending multiple similar requests in quick succession",
        ]
        
        details = {
            "limit_type": limit_type,
            "reset_in_seconds": reset_in,
        }
        
        return ErrorResponse(
            error_type=ErrorType.RATE_LIMIT_ERROR,
            message=message,
            recovery_suggestions=suggestions,
            error_details=details,
        )
    
    @staticmethod
    def system_error(action: str, error_details: Optional[str] = None, ticket_id: Optional[str] = None) -> ErrorResponse:
        """
        Handle system error gracefully
        
        Args:
            action: Action that failed
            error_details: Technical error details (for logging)
            ticket_id: Support ticket ID if available
        
        Returns:
            ErrorResponse with support contact
        """
        message = (
            f"Something went wrong while {action}. "
            f"Our team has been notified and is working on it. "
            f"Please try again in a few moments."
        )
        
        if ticket_id:
            message += f"\nReference: {ticket_id}"
        
        suggestions = [
            "Try again in a few moments",
            "Check your internet connection",
            "Clear your browser cache and reload",
            f"If the problem persists, contact support@bank.com with reference: {ticket_id or 'System Error'}",
        ]
        
        details = None
        if error_details:
            details = {"technical_error": error_details}
        
        return ErrorResponse(
            error_type=ErrorType.SYSTEM_ERROR,
            message=message,
            recovery_suggestions=suggestions,
            error_details=details,
            support_ticket_id=ticket_id,
        )
    
    @staticmethod
    def authentication_error(reason: str) -> ErrorResponse:
        """
        Handle authentication errors
        
        Args:
            reason: Reason for authentication failure
        
        Returns:
            ErrorResponse with recovery steps
        """
        message = f"Authentication failed: {reason}"
        
        suggestions = [
            "Verify your login credentials and try again",
            "Reset your password if you've forgotten it",
            "Check that you're using the correct bank account",
            "Contact support if you continue to experience issues",
        ]
        
        return ErrorResponse(
            error_type=ErrorType.AUTHENTICATION_ERROR,
            message=message,
            recovery_suggestions=suggestions,
        )
    
    @staticmethod
    def negation_detected_error(entity: str, negated_value: str) -> ErrorResponse:
        """
        Handle negation detection (e.g., "don't use savings")
        
        Args:
            entity: Entity that was negated
            negated_value: The value that should NOT be used
        
        Returns:
            ErrorResponse asking for clarification
        """
        message = (
            f"I understand you don't want to use {negated_value}. "
            f"Please clarify which {entity} you'd like to use instead."
        )
        
        suggestions = [
            f"Specify a different {entity}",
            f"Say something like 'Use my {entity.replace('account', 'checking account')} instead'",
            "List your available accounts if needed",
        ]
        
        return ErrorResponse(
            error_type=ErrorType.BUSINESS_LOGIC_ERROR,
            message=message,
            recovery_suggestions=suggestions,
        )
    
    @staticmethod
    def get_recovery_suggestion(error_type: str, context: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Get recovery suggestions for a generic error
        
        Args:
            error_type: Type of error (string key)
            context: Error context with details
        
        Returns:
            (message: str, suggestions: List[str])
        """
        message = "An error occurred. Here's what you can do:"
        
        suggestions_map = {
            "input_validation": [
                "Please check your input and try again",
                "Use the correct format (e.g., numbers for amounts)",
                "Avoid special characters unless necessary",
            ],
            "network_error": [
                "Check your internet connection",
                "Try again in a moment",
                "If the problem persists, try refreshing the page",
            ],
            "database_error": [
                "Try again in a few moments",
                "If the problem continues, contact support",
                "Your request may have been processed despite the error message",
            ],
            "timeout": [
                "The request took too long. Try again.",
                "Check your internet connection",
                "Simplify your request if possible",
            ],
            "unknown": [
                "Try again",
                "Contact support@bank.com if the problem continues",
                "Provide the error details to support for faster help",
            ],
        }
        
        suggestions = suggestions_map.get(error_type, suggestions_map["unknown"])
        
        return message, suggestions
    
    @staticmethod
    def handle_exception(exception: Exception, action: str = "processing your request") -> ErrorResponse:
        """
        Convert exception to user-friendly error response
        
        Args:
            exception: Exception that occurred
            action: What action was being performed
        
        Returns:
            ErrorResponse appropriate for the exception type
        """
        exc_type = type(exception).__name__
        exc_message = str(exception)
        
        # Map common exceptions to user-friendly responses
        if "ValueError" in exc_type:
            return ErrorRecovery.validation_error("input", str(exception), "Invalid format or value")
        elif "KeyError" in exc_type:
            return ErrorRecovery.system_error(action, f"Missing required field: {exc_message}")
        elif "DatabaseError" in exc_type or "sqlite" in exc_type.lower():
            return ErrorRecovery.system_error(action, "Database connection issue")
        else:
            return ErrorRecovery.system_error(action, f"{exc_type}: {exc_message}")
