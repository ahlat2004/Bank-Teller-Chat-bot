"""
Validation Layer - Input validation and rate limiting
Fixes Flaws: #13 (No Rate Limiting), #19 (DoS Vulnerability)
"""

import re
from typing import Tuple, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import html
import bleach


class RequestValidator:
    """Validates incoming chat requests for format, encoding, and security"""
    
    # Configuration
    MIN_MESSAGE_LENGTH = 1
    MAX_MESSAGE_LENGTH = 1000
    ALLOWED_TAGS = []  # No HTML tags allowed
    ALLOWED_ATTRIBUTES = {}
    
    @staticmethod
    def validate_message(message: str) -> Tuple[bool, str]:
        """
        Comprehensive message validation
        Returns: (is_valid: bool, error_message: str)
        """
        if not message:
            return False, "Message cannot be empty."
        
        # Check length
        if len(message) < RequestValidator.MIN_MESSAGE_LENGTH:
            return False, f"Message is too short (minimum {RequestValidator.MIN_MESSAGE_LENGTH} character)."
        
        if len(message) > RequestValidator.MAX_MESSAGE_LENGTH:
            return False, f"Message is too long (maximum {RequestValidator.MAX_MESSAGE_LENGTH} characters). Please shorten your message."
        
        # Check encoding
        if not RequestValidator.validate_encoding(message):
            return False, "Message contains invalid characters. Please use standard text only."
        
        return True, ""
    
    @staticmethod
    def validate_encoding(message: str) -> bool:
        """Check if message is valid UTF-8 and doesn't contain invalid control characters"""
        try:
            # Try to encode/decode to verify UTF-8
            message.encode('utf-8').decode('utf-8')
            
            # Check for invalid control characters (except newlines and tabs)
            for char in message:
                code = ord(char)
                # Allow: letters, digits, punctuation, spaces, newlines, tabs
                # Disallow: other control characters
                if code < 32 and code not in (9, 10, 13):  # tab, newline, carriage return
                    return False
            
            return True
        except (UnicodeDecodeError, UnicodeEncodeError):
            return False
    
    @staticmethod
    def sanitize_sql_injection(message: str) -> str:
        """
        Remove/escape SQL injection patterns
        NOTE: Primary protection is parameterized queries, this is defense-in-depth
        """
        dangerous_patterns = [
            r";\s*DROP\s+TABLE",
            r";\s*DELETE\s+FROM",
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"' OR '1'='1",
            r'" OR "1"="1',
            r"--.*$",
            r"/\*.*\*/",
        ]
        
        result = message
        for pattern in dangerous_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE | re.MULTILINE)
        
        return result
    
    @staticmethod
    def sanitize_xss(message: str) -> str:
        """
        Remove XSS attack patterns
        NOTE: Primary protection is output encoding, this is defense-in-depth
        """
        # Escape HTML entities
        sanitized = html.escape(message)
        
        # Remove script tags and event handlers
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'\son\w+\s*=', '', sanitized, flags=re.IGNORECASE)  # Remove onclick, onerror, etc.
        
        # Use bleach library for additional sanitization
        sanitized = bleach.clean(sanitized, tags=[], strip=True)
        
        return sanitized
    
    @staticmethod
    def sanitize_input(message: str) -> str:
        """Apply all sanitization steps"""
        sanitized = RequestValidator.sanitize_sql_injection(message)
        sanitized = RequestValidator.sanitize_xss(sanitized)
        return sanitized.strip()


class RateLimiter:
    """
    Rate limiting to prevent DoS attacks
    Tracks requests per user per minute/hour/day
    Fixes Flaw: #13 (No Rate Limiting), #19 (DoS Vulnerability)
    """
    
    # Configuration - tunable based on production needs
    MAX_REQUESTS_PER_MINUTE = 10
    MAX_REQUESTS_PER_HOUR = 100
    MAX_REQUESTS_PER_DAY = 1000
    
    def __init__(self):
        """Initialize rate limiter with in-memory tracking"""
        # Structure: {user_id: {session_id: [timestamp1, timestamp2, ...]}}
        self.request_history: Dict[int, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self.cleanup_interval = 300  # seconds - cleanup old entries
        self.last_cleanup = datetime.now()
    
    def check_rate_limit(self, user_id: int, session_id: str) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limits
        Returns: (is_allowed: bool, message: str)
        """
        now = datetime.now()
        
        # Periodic cleanup of old entries
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = now
        
        # Get user's request history
        user_sessions = self.request_history[user_id]
        session_requests = user_sessions[session_id]
        
        # Remove old requests outside the tracking window
        cutoff_day = now - timedelta(days=1)
        session_requests[:] = [ts for ts in session_requests if ts > cutoff_day]
        
        # Check per-minute limit
        cutoff_minute = now - timedelta(minutes=1)
        minute_requests = [ts for ts in session_requests if ts > cutoff_minute]
        
        if len(minute_requests) >= self.MAX_REQUESTS_PER_MINUTE:
            remaining = int((min(minute_requests) + timedelta(minutes=1) - now).total_seconds())
            return False, f"Too many requests. Please try again in {remaining} seconds."
        
        # Check per-hour limit
        cutoff_hour = now - timedelta(hours=1)
        hour_requests = [ts for ts in session_requests if ts > cutoff_hour]
        
        if len(hour_requests) >= self.MAX_REQUESTS_PER_HOUR:
            remaining_minutes = int((min(hour_requests) + timedelta(hours=1) - now).total_seconds() / 60)
            return False, f"Too many requests. Please try again in {remaining_minutes} minutes."
        
        # Check per-day limit
        day_requests = session_requests
        
        if len(day_requests) >= self.MAX_REQUESTS_PER_DAY:
            remaining_hours = int((min(day_requests) + timedelta(days=1) - now).total_seconds() / 3600)
            return False, f"Daily request limit exceeded. Please try again in {remaining_hours} hours."
        
        # All checks passed - allow request
        return True, ""
    
    def track_request(self, user_id: int, session_id: str) -> None:
        """Record a request from user"""
        self.request_history[user_id][session_id].append(datetime.now())
    
    def get_remaining_requests(self, user_id: int, session_id: str) -> Dict[str, int]:
        """Get remaining request count for user at current time"""
        now = datetime.now()
        
        session_requests = self.request_history[user_id][session_id]
        session_requests[:] = [ts for ts in session_requests if ts > (now - timedelta(days=1))]
        
        cutoff_minute = now - timedelta(minutes=1)
        minute_requests = [ts for ts in session_requests if ts > cutoff_minute]
        
        cutoff_hour = now - timedelta(hours=1)
        hour_requests = [ts for ts in session_requests if ts > cutoff_hour]
        
        return {
            "per_minute": max(0, self.MAX_REQUESTS_PER_MINUTE - len(minute_requests)),
            "per_hour": max(0, self.MAX_REQUESTS_PER_HOUR - len(hour_requests)),
            "per_day": max(0, self.MAX_REQUESTS_PER_DAY - len(session_requests)),
        }
    
    def _cleanup_old_entries(self) -> None:
        """Remove request history older than 1 day to free memory"""
        cutoff = datetime.now() - timedelta(days=1)
        
        for user_id in list(self.request_history.keys()):
            for session_id in list(self.request_history[user_id].keys()):
                requests = self.request_history[user_id][session_id]
                requests[:] = [ts for ts in requests if ts > cutoff]
                
                # Clean up empty sessions
                if not requests:
                    del self.request_history[user_id][session_id]
            
            # Clean up empty users
            if not self.request_history[user_id]:
                del self.request_history[user_id]
    
    def reset(self) -> None:
        """Reset all rate limit tracking (useful for testing)"""
        self.request_history.clear()


# Global rate limiter instance
rate_limiter = RateLimiter()
request_validator = RequestValidator()
