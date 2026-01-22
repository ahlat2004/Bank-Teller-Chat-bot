"""
Session Manager
Manages user sessions and dialogue states
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import uuid
from ml.dialogue.dialogue_state import DialogueState
import threading
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages conversation sessions
    Stores dialogue states in memory with automatic cleanup
    """
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize session manager
        
        Args:
            session_timeout_minutes: Session timeout in minutes
        """
        self.sessions: Dict[str, DialogueState] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def create_session(self, user_id: int) -> str:
        """
        Create a new session
        
        Args:
            user_id: User identifier
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        with self.lock:
            state = DialogueState(user_id=user_id, session_id=session_id)
            self.sessions[session_id] = state
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[DialogueState]:
        """
        Get session state
        
        Args:
            session_id: Session identifier
            
        Returns:
            DialogueState or None if not found
        """
        with self.lock:
            state = self.sessions.get(session_id)
            
            if state:
                # Check if session expired
                time_since_update = datetime.now() - state.last_updated
                if time_since_update > self.session_timeout:
                    # Session expired, remove it
                    del self.sessions[session_id]
                    return None
            
            return state
    
    def save_session(self, session_id: str, state: DialogueState):
        """
        Save session state
        
        Args:
            session_id: Session identifier
            state: Dialogue state to save
        """
        with self.lock:
            state.last_updated = datetime.now()
            self.sessions[session_id] = state
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False
    
    def get_user_sessions(self, user_id: int) -> list:
        """
        Get all active sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session IDs
        """
        with self.lock:
            return [
                session_id 
                for session_id, state in self.sessions.items()
                if state.user_id == user_id
            ]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        with self.lock:
            now = datetime.now()
            expired = [
                session_id
                for session_id, state in self.sessions.items()
                if now - state.last_updated > self.session_timeout
            ]
            
            for session_id in expired:
                del self.sessions[session_id]
            
            if expired:
                logger.info(f"🧹 Cleaned up {len(expired)} expired sessions")

    def clear_all_sessions(self) -> int:
        """Clear all sessions from memory and return the number cleared"""
        with self.lock:
            count = len(self.sessions)
            self.sessions.clear()
        if count:
            logger.info(f"🧹 Cleared all sessions ({count}) via clear_all_sessions")
        return count
    
    def _start_cleanup_thread(self):
        """Start background thread for session cleanup"""
        def cleanup_loop():
            import time
            while True:
                time.sleep(300)  # Run every 5 minutes
                self.cleanup_expired_sessions()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        with self.lock:
            return len(self.sessions)
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        with self.lock:
            return {
                'total_sessions': len(self.sessions),
                'sessions_by_status': self._count_by_status(),
                'timeout_minutes': self.session_timeout.total_seconds() / 60
            }
    
    def _count_by_status(self) -> Dict[str, int]:
        """Count sessions by status"""
        status_counts = {}
        for state in self.sessions.values():
            status = state.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "SESSION MANAGER TEST")
    print("=" * 70)
    
    # Initialize session manager
    sm = SessionManager(session_timeout_minutes=30)
    print("\n✅ Session manager initialized")
    print(f"   Timeout: 30 minutes")
    
    # Create sessions
    print("\n📝 Creating sessions:")
    session1 = sm.create_session(user_id=1)
    print(f"   Session 1: {session1}")
    
    session2 = sm.create_session(user_id=1)
    print(f"   Session 2: {session2}")
    
    session3 = sm.create_session(user_id=2)
    print(f"   Session 3: {session3}")
    
    # Get session
    print("\n📂 Retrieving session:")
    state = sm.get_session(session1)
    print(f"   Retrieved: {state}")
    
    # Modify and save
    print("\n💾 Modifying and saving session:")
    state.set_intent("transfer_money", 0.95)
    sm.save_session(session1, state)
    print(f"   Intent set: {state.intent}")
    
    # Get user sessions
    print("\n👤 User 1 sessions:")
    user1_sessions = sm.get_user_sessions(1)
    print(f"   Found {len(user1_sessions)} sessions")
    
    # Get stats
    print("\n📊 Session statistics:")
    stats = sm.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✅ Session manager tests complete!")