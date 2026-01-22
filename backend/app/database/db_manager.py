"""
Database Manager
Handles database connections and operations
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from datetime import datetime
import json


class DatabaseManager:
    """
    Manages SQLite database connections and operations
    """
    
    def __init__(self, db_path: str = 'data/bank_demo.db'):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database if needed
        if not os.path.exists(db_path):
            print(f"[DB] Creating new database at {db_path}")
            self._initialize_database()
        else:
            print(f"[DB] Using existing database at {db_path}")
        
        # Initialize auth tables
        self.initialize_auth_tables()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Initialize database with schema"""
        # Try multiple possible paths for schema.sql
        possible_paths = [
            os.path.join('backend', 'app', 'database', 'schema.sql'),
            os.path.join(os.path.dirname(__file__), 'schema.sql'),
            'schema.sql'
        ]
        
        schema_path = None
        for path in possible_paths:
            if os.path.exists(path):
                schema_path = path
                break
        
        if schema_path:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
            
            print("[OK] Database schema created")
        else:
            print(f"[WARN] Schema file not found. Tried paths:")
            for path in possible_paths:
                print(f"     - {path}")
    
    def seed_database(self):
        """Seed database with demo data"""
        # Try multiple possible paths for seed_data.sql
        possible_paths = [
            os.path.join('backend', 'app', 'database', 'seed_data.sql'),
            os.path.join(os.path.dirname(__file__), 'seed_data.sql'),
            'seed_data.sql'
        ]
        
        seed_path = None
        for path in possible_paths:
            if os.path.exists(path):
                seed_path = path
                break
        
        if seed_path:
            with open(seed_path, 'r') as f:
                seed_sql = f.read()
            
            with self.get_connection() as conn:
                conn.executescript(seed_sql)
            
            print("[OK] Database seeded with demo data")
            return True
        else:
            print(f"[WARN] Seed file not found. Tried paths:")
            for path in possible_paths:
                print(f"     - {path}")
            return False
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """
        Execute a SELECT query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount
    
    # ========== AUDIT LOGGING OPERATIONS ==========
    
    def apply_phase2_migration(self) -> bool:
        """
        Apply Phase 2 migration to add audit logging tables
        
        Returns:
            True if migration successful, False otherwise
        """
        try:
            # Create tables directly instead of using migration file
            with self.get_connection() as conn:
                try:
                    # Create audit_log table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS audit_log (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            session_id TEXT NOT NULL,
                            intent TEXT NOT NULL,
                            action TEXT NOT NULL,
                            input_data TEXT,
                            output_data TEXT,
                            status TEXT NOT NULL,
                            error_message TEXT,
                            idempotency_key TEXT UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                    """)
                    print("[OK] audit_log table created")
                except Exception as e:
                    print(f"[WARN] audit_log table: {str(e)}")
                
                try:
                    # Create indexes for audit_log
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_log(session_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_idempotency ON audit_log(idempotency_key)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at DESC)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_intent ON audit_log(intent)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_status ON audit_log(status)")
                    print("[OK] audit_log indexes created")
                except Exception as e:
                    print(f"[WARN] audit_log indexes: {str(e)}")
                
                try:
                    # Modify transactions table
                    conn.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS idempotency_key TEXT UNIQUE")
                    print("[OK] transactions.idempotency_key added")
                except Exception as e:
                    print(f"[WARN] transactions.idempotency_key: {str(e)}")
                
                try:
                    conn.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS audit_log_id INTEGER")
                    print("[OK] transactions.audit_log_id added")
                except Exception as e:
                    print(f"[WARN] transactions.audit_log_id: {str(e)}")
                
                try:
                    conn.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'completed'")
                    print("[OK] transactions.status added")
                except Exception as e:
                    print(f"[WARN] transactions.status: {str(e)}")
                
                try:
                    conn.execute("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS rollback_data TEXT")
                    print("[OK] transactions.rollback_data added")
                except Exception as e:
                    print(f"[WARN] transactions.rollback_data: {str(e)}")
                
                try:
                    # Create indexes for transactions
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_idempotency ON transactions(idempotency_key)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_audit ON transactions(audit_log_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_status ON transactions(status)")
                    print("[OK] transactions indexes created")
                except Exception as e:
                    print(f"[WARN] transactions indexes: {str(e)}")
                
                try:
                    # Create sessions table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS sessions (
                            id TEXT PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            state_json TEXT,
                            current_intent TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP,
                            status TEXT DEFAULT 'active',
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                    """)
                    print("[OK] sessions table created")
                except Exception as e:
                    print(f"[WARN] sessions table: {str(e)}")
                
                try:
                    # Create indexes for sessions
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
                    print("[OK] sessions indexes created")
                except Exception as e:
                    print(f"[WARN] sessions indexes: {str(e)}")
                
                try:
                    # Create idempotency_cache table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS idempotency_cache (
                            idempotency_key TEXT PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            result_data TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                    """)
                    print("[OK] idempotency_cache table created")
                except Exception as e:
                    print(f"[WARN] idempotency_cache table: {str(e)}")
                
                try:
                    # Create indexes for idempotency_cache
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_idempotency_user ON idempotency_cache(user_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_idempotency_expires ON idempotency_cache(expires_at)")
                    print("[OK] idempotency_cache indexes created")
                except Exception as e:
                    print(f"[WARN] idempotency_cache indexes: {str(e)}")
            
            print("[OK] Phase 2 migration applied successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Phase 2 migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def log_audit(self, user_id: int, session_id: str, intent: str, action: str,
                  input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]],
                  status: str, idempotency_key: str, error_msg: Optional[str] = None) -> Optional[int]:
        """
        Log an action to the audit log
        
        Args:
            user_id: User ID
            session_id: Session ID
            intent: Intent name
            action: Action name
            input_data: Input data (dict)
            output_data: Output data (dict)
            status: Status (success, failure, pending, rolled_back)
            idempotency_key: Unique idempotency key
            error_msg: Error message if failed
            
        Returns:
            Audit log ID if successful, None otherwise
        """
        try:
            query = """
                INSERT INTO audit_log 
                (user_id, session_id, intent, action, input_data, output_data, status, error_message, idempotency_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            input_json = json.dumps(input_data) if input_data else '{}'
            output_json = json.dumps(output_data) if output_data else None
            
            with self.get_connection() as conn:
                cursor = conn.execute(query, (
                    user_id, session_id, intent, action,
                    input_json, output_json, status, error_msg, idempotency_key
                ))
                audit_id = cursor.lastrowid
            
            return audit_id
        except Exception as e:
            print(f"[ERROR] Failed to log audit: {str(e)}")
            return None
    
    def get_audit_by_idempotency(self, idempotency_key: str) -> Optional[Dict]:
        """
        Get audit log entry by idempotency key
        
        Args:
            idempotency_key: Idempotency key to look up
            
        Returns:
            Audit log entry dict, or None if not found
        """
        try:
            query = "SELECT * FROM audit_log WHERE idempotency_key = ?"
            results = self.execute_query(query, (idempotency_key,))
            return results[0] if results else None
        except Exception as e:
            print(f"[ERROR] Failed to get audit by idempotency: {str(e)}")
            return None
    
    def get_audit_by_user(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get audit log entries for a user
        
        Args:
            user_id: User ID
            limit: Number of recent entries to return
            
        Returns:
            List of audit log entries
        """
        try:
            query = """
                SELECT * FROM audit_log 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """
            return self.execute_query(query, (user_id, limit))
        except Exception as e:
            print(f"[ERROR] Failed to get audit by user: {str(e)}")
            return []
    
    def get_audit_by_session(self, session_id: str) -> List[Dict]:
        """
        Get audit log entries for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of audit log entries for the session
        """
        try:
            query = """
                SELECT * FROM audit_log 
                WHERE session_id = ? 
                ORDER BY created_at ASC
            """
            return self.execute_query(query, (session_id,))
        except Exception as e:
            print(f"[ERROR] Failed to get audit by session: {str(e)}")
            return []
    
    def mark_transaction_rolled_back(self, transaction_id: int) -> bool:
        """
        Mark a transaction as rolled back
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = "UPDATE transactions SET status = 'rolled_back' WHERE id = ?"
            self.execute_update(query, (transaction_id,))
            return True
        except Exception as e:
            print(f"[ERROR] Failed to mark transaction rolled back: {str(e)}")
            return False
    
    # ========== SESSION OPERATIONS ==========
    
    def create_session(self, user_id: int, session_id: Optional[str] = None) -> str:
        """
        Create a new session
        
        Args:
            user_id: User ID
            session_id: Optional session ID (generated if not provided)
            
        Returns:
            Session ID
        """
        import uuid
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            query = """
                INSERT INTO sessions (id, user_id, status)
                VALUES (?, ?, 'active')
            """
            with self.get_connection() as conn:
                conn.execute(query, (session_id, user_id))
            
            return session_id
        except Exception as e:
            print(f"[WARN] Session creation failed: {str(e)}. Returning new UUID.")
            return str(uuid.uuid4())
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session (clears chat history)
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            query = "DELETE FROM sessions WHERE id = ?"
            with self.get_connection() as conn:
                cursor = conn.execute(query, (session_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[ERROR] Session deletion failed: {str(e)}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID
            
        Returns:
            Session dict or None
        """
        try:
            query = "SELECT * FROM sessions WHERE id = ?"
            results = self.execute_query(query, (session_id,))
            return results[0] if results else None
        except Exception as e:
            print(f"[ERROR] Failed to get session: {str(e)}")
            return None
    
    def update_session_state(self, session_id: str, state_json: str, current_intent: Optional[str] = None) -> bool:
        """
        Update session state
        
        Args:
            session_id: Session ID
            state_json: State as JSON string
            current_intent: Current intent
            
        Returns:
            True if successful
        """
        try:
            query = """
                UPDATE sessions 
                SET state_json = ?, current_intent = ?, last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            self.execute_update(query, (state_json, current_intent, session_id))
            return True
        except Exception as e:
            print(f"[ERROR] Failed to update session state: {str(e)}")
            return False
    
    # ========== USER OPERATIONS ==========
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        """Get user by phone number"""
        query = "SELECT * FROM users WHERE phone = ?"
        results = self.execute_query(query, (phone,))
        return results[0] if results else None
    
    def create_user(self, name: str, phone: str, email: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Create a new user in the system
        
        Args:
            name: User's full name
            phone: User's phone number (must be unique)
            email: User's email address (optional)
            
        Returns:
            Tuple of (success, message, user_id)
        """
        # Check if phone already exists
        existing_user = self.get_user_by_phone(phone)
        if existing_user:
            return False, f"User with phone {phone} already exists", None
        
        try:
            query = """
                INSERT INTO users (name, phone, email)
                VALUES (?, ?, ?)
            """
            with self.get_connection() as conn:
                cursor = conn.execute(query, (name, phone, email))
                user_id = cursor.lastrowid
            
            return True, f"User {name} created successfully", user_id
        except Exception as e:
            return False, f"Failed to create user: {str(e)}", None
    
    # ========== ACCOUNT OPERATIONS ==========
    
    def get_user_accounts(self, user_id: int) -> List[Dict]:
        """Get all accounts for a user"""
        query = """
            SELECT * FROM accounts 
            WHERE user_id = ? AND status = 'active'
            ORDER BY account_type
        """
        return self.execute_query(query, (user_id,))
    
    def get_account_by_number(self, account_no: str) -> Optional[Dict]:
        """Get account by account number"""
        query = "SELECT * FROM accounts WHERE account_no = ?"
        results = self.execute_query(query, (account_no,))
        return results[0] if results else None
    
    def get_balance(self, account_no: str) -> Optional[float]:
        """Get account balance"""
        account = self.get_account_by_number(account_no)
        return account['balance'] if account else None
    
    def update_balance(self, account_no: str, new_balance: float) -> bool:
        """Update account balance"""
        query = """
            UPDATE accounts 
            SET balance = ?, updated_at = CURRENT_TIMESTAMP
            WHERE account_no = ?
        """
        rows_affected = self.execute_update(query, (new_balance, account_no))
        return rows_affected > 0
    
    def create_account(self, user_id: int, account_type: str, 
                      initial_balance: float = 0.0) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new account for a user
        
        Args:
            user_id: ID of the user
            account_type: Type of account (savings, current, salary)
            initial_balance: Initial balance (default 0)
            
        Returns:
            Tuple of (success, message, account_number)
        """
        # Verify user exists
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found", None
        
        # Validate account type
        valid_types = ['savings', 'current', 'salary']
        if account_type not in valid_types:
            return False, f"Invalid account type. Must be one of: {', '.join(valid_types)}", None
        
        # Generate unique account number
        import uuid
        import random
        timestamp = int(__import__('time').time() * 1000) % 1000000
        account_no = f"PK{user_id:02d}{account_type[:3].upper()}{timestamp}{random.randint(1000, 9999)}"
        
        try:
            query = """
                INSERT INTO accounts (user_id, account_no, account_type, balance, status)
                VALUES (?, ?, ?, ?, 'active')
            """
            with self.get_connection() as conn:
                conn.execute(query, (user_id, account_no, account_type, initial_balance))
            
            return True, f"{account_type.capitalize()} account created successfully", account_no
        except Exception as e:
            return False, f"Failed to create account: {str(e)}", None
    
    # ========== TRANSACTION OPERATIONS ==========
    
    def record_transaction(self, account_id: int, txn_type: str, 
                          amount: float, payee: Optional[str] = None,
                          description: Optional[str] = None,
                          balance_after: Optional[float] = None,
                          meta: Optional[Dict] = None) -> int:
        """
        Record a transaction
        
        Args:
            account_id: Account ID
            txn_type: Transaction type (credit, debit, transfer_in, transfer_out)
            amount: Transaction amount
            payee: Payee name
            description: Transaction description
            balance_after: Balance after transaction
            meta: Additional metadata as JSON
            
        Returns:
            Transaction ID
        """
        query = """
            INSERT INTO transactions 
            (account_id, type, amount, payee, description, balance_after, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        meta_json = json.dumps(meta) if meta else None
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (
                account_id, txn_type, amount, payee, 
                description, balance_after, meta_json
            ))
            return cursor.lastrowid
    
    def get_transaction_history(self, account_id: int, limit: int = 10) -> List[Dict]:
        """Get transaction history for an account"""
        query = """
            SELECT * FROM transactions 
            WHERE account_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        return self.execute_query(query, (account_id, limit))
    
    def get_recent_transactions_by_account_no(self, account_no: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions by account number"""
        query = """
            SELECT t.* FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.account_no = ?
            ORDER BY t.timestamp DESC
            LIMIT ?
        """
        return self.execute_query(query, (account_no, limit))
    
    # ========== TRANSFER OPERATIONS ==========
    
    def execute_transfer(self, from_account_no: str, to_account_no: str, 
                        amount: float, description: str = "Transfer") -> Tuple[bool, str]:
        """
        Execute money transfer between accounts
        
        Args:
            from_account_no: Source account number
            to_account_no: Destination account number
            amount: Transfer amount
            description: Transfer description
            
        Returns:
            Tuple of (success, message)
        """
        # Get source account
        from_account = self.get_account_by_number(from_account_no)
        if not from_account:
            return False, "Source account not found"
        
        # Get destination account
        to_account = self.get_account_by_number(to_account_no)
        if not to_account:
            return False, "Destination account not found"
        
        # Check sufficient balance
        if from_account['balance'] < amount:
            return False, "Insufficient balance"
        
        # Calculate new balances
        new_from_balance = from_account['balance'] - amount
        new_to_balance = to_account['balance'] + amount
        
        try:
            with self.get_connection() as conn:
                # Update source account balance
                conn.execute(
                    "UPDATE accounts SET balance = ? WHERE account_no = ?",
                    (new_from_balance, from_account_no)
                )
                
                # Update destination account balance
                conn.execute(
                    "UPDATE accounts SET balance = ? WHERE account_no = ?",
                    (new_to_balance, to_account_no)
                )
                
                # Record debit transaction for source
                conn.execute("""
                    INSERT INTO transactions 
                    (account_id, type, amount, payee, description, balance_after)
                    VALUES (?, 'transfer_out', ?, ?, ?, ?)
                """, (from_account['id'], amount, to_account['account_no'], 
                      description, new_from_balance))
                
                # Record credit transaction for destination
                conn.execute("""
                    INSERT INTO transactions 
                    (account_id, type, amount, payee, description, balance_after)
                    VALUES (?, 'transfer_in', ?, ?, ?, ?)
                """, (to_account['id'], amount, from_account['account_no'], 
                      description, new_to_balance))
                
                conn.commit()
            
            return True, f"Successfully transferred PKR {amount:,.2f}"
            
        except Exception as e:
            return False, f"Transfer failed: {str(e)}"
    
    # ========== BILL OPERATIONS ==========
    
    def get_user_bills(self, user_id: int, status: str = 'unpaid') -> List[Dict]:
        """Get bills for a user"""
        query = """
            SELECT * FROM bills 
            WHERE user_id = ? AND status = ?
            ORDER BY due_date
        """
        return self.execute_query(query, (user_id, status))
    
    def get_bill_by_type(self, user_id: int, bill_type: str) -> Optional[Dict]:
        """Get unpaid bill by type"""
        query = """
            SELECT * FROM bills 
            WHERE user_id = ? AND type = ? AND status = 'unpaid'
            ORDER BY due_date
            LIMIT 1
        """
        results = self.execute_query(query, (user_id, bill_type))
        return results[0] if results else None
    
    def pay_bill(self, user_id: int, bill_type: str, amount: float,
                account_no: str) -> Tuple[bool, str]:
        """
        Pay a bill
        
        Args:
            user_id: User ID
            bill_type: Type of bill
            amount: Payment amount
            account_no: Account to debit from
            
        Returns:
            Tuple of (success, message)
        """
        # Get account
        account = self.get_account_by_number(account_no)
        if not account:
            return False, "Account not found"
        
        # Check account ownership
        if account['user_id'] != user_id:
            return False, "Account does not belong to user"
        
        # Check sufficient balance
        if account['balance'] < amount:
            return False, "Insufficient balance"
        
        # Get bill
        bill = self.get_bill_by_type(user_id, bill_type)
        
        try:
            with self.get_connection() as conn:
                # Deduct from account
                new_balance = account['balance'] - amount
                conn.execute(
                    "UPDATE accounts SET balance = ? WHERE account_no = ?",
                    (new_balance, account_no)
                )
                
                # Record transaction
                conn.execute("""
                    INSERT INTO transactions 
                    (account_id, type, amount, description, balance_after)
                    VALUES (?, 'debit', ?, ?, ?)
                """, (account['id'], amount, f"{bill_type.title()} bill payment", 
                      new_balance))
                
                # Update bill status if exists
                if bill:
                    conn.execute("""
                        UPDATE bills 
                        SET status = 'paid', paid_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (bill['id'],))
                
                conn.commit()
            
            return True, f"Successfully paid {bill_type} bill of PKR {amount:,.2f}"
            
        except Exception as e:
            return False, f"Bill payment failed: {str(e)}"
    
    # ========== CARD OPERATIONS ==========
    
    def get_user_cards(self, user_id: int) -> List[Dict]:
        """Get all cards for a user"""
        query = """
            SELECT c.* FROM cards c
            JOIN accounts a ON c.account_id = a.id
            WHERE a.user_id = ?
            ORDER BY c.card_type, c.created_at DESC
        """
        return self.execute_query(query, (user_id,))
    
    def block_card(self, card_number: str) -> Tuple[bool, str]:
        """Block a card"""
        query = "UPDATE cards SET status = 'blocked' WHERE card_number = ?"
        rows_affected = self.execute_update(query, (card_number,))
        
        if rows_affected > 0:
            return True, "Card blocked successfully"
        else:
            return False, "Card not found"
    
    # ========== AUTH-RELATED METHODS (NEW) ==========
    
    def check_email_exists(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email to check
            
        Returns:
            True if exists
        """
        query = "SELECT COUNT(*) FROM users WHERE email = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(query, (email,))
            count = cursor.fetchone()[0]
            return count > 0
    
    def initialize_auth_tables(self):
        """Initialize authentication tables (OTP sessions)"""
        schema_auth_path = os.path.join('backend', 'app', 'database', 'schema_auth.sql')
        
        if os.path.exists(schema_auth_path):
            with open(schema_auth_path, 'r') as f:
                schema_sql = f.read()
            
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
            
            print("[OK] Authentication tables initialized")
            return True
        else:
            print(f"[WARN] Auth schema file not found at {schema_auth_path}")
            # Create tables inline if file not found
            self._create_auth_tables_inline()
            return True
    
    def _create_auth_tables_inline(self):
        """Create auth tables directly (fallback)"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS otp_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    otp_code TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    verified BOOLEAN DEFAULT FALSE,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS verified_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    user_id INTEGER,
                    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    purpose TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            print("[OK] Authentication tables created inline")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print(" " * 20 + "DATABASE MANAGER TEST")
    print("=" * 70)
    
    # Initialize database
    db = DatabaseManager('data/bank_demo_test.db')
    
    # Seed database
    print("\n📦 Seeding database...")
    db.seed_database()
    
    # Test user operations
    print("\n👤 Testing User Operations:")
    print("-" * 70)
    user = db.get_user_by_id(1)
    print(f"User 1: {user['name']} ({user['phone']})")
    
    # Test account operations
    print("\n🏦 Testing Account Operations:")
    print("-" * 70)
    accounts = db.get_user_accounts(1)
    for acc in accounts:
        print(f"  {acc['account_type']:10s} - {acc['account_no']:30s} - PKR {acc['balance']:,.2f}")
    
    # Test balance check
    print("\n💰 Testing Balance Check:")
    print("-" * 70)
    balance = db.get_balance(accounts[0]['account_no'])
    print(f"Balance: PKR {balance:,.2f}")
    
    # Test transaction history
    print("\n📜 Testing Transaction History:")
    print("-" * 70)
    transactions = db.get_recent_transactions_by_account_no(accounts[0]['account_no'], 5)
    for txn in transactions:
        print(f"  {txn['type']:15s} PKR {txn['amount']:>10,.2f} - {txn['description']}")
    
    # Test bills
    print("\n🧾 Testing Bill Operations:")
    print("-" * 70)
    bills = db.get_user_bills(1, 'unpaid')
    for bill in bills:
        print(f"  {bill['type']:15s} PKR {bill['amount']:>8,.2f} - Due: {bill['due_date']}")
    
    print("\n" + "=" * 70)
    print("✅ Database manager tests complete!")