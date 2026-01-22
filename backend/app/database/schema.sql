-- Bank Teller Chatbot Database Schema
-- SQLite Database for Demo Banking System

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts Table
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_no TEXT UNIQUE NOT NULL,
    account_type TEXT NOT NULL CHECK(account_type IN ('savings', 'current', 'salary')),
    balance REAL DEFAULT 0.0 CHECK(balance >= 0),
    currency TEXT DEFAULT 'PKR',
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'frozen', 'closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('credit', 'debit', 'transfer_in', 'transfer_out')),
    amount REAL NOT NULL CHECK(amount > 0),
    payee TEXT,
    description TEXT,
    balance_after REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meta TEXT,
    idempotency_key TEXT UNIQUE,
    audit_log_id INTEGER,
    status TEXT DEFAULT 'completed',
    rollback_data TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- Bills Table
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('electricity', 'mobile', 'gas', 'water', 'internet', 'credit_card', 'loan')),
    amount REAL NOT NULL CHECK(amount > 0),
    due_date DATE NOT NULL,
    status TEXT DEFAULT 'unpaid' CHECK(status IN ('unpaid', 'paid', 'overdue')),
    reference_no TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Cards Table
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    card_number TEXT UNIQUE NOT NULL,
    card_type TEXT NOT NULL CHECK(card_type IN ('debit', 'credit', 'prepaid')),
    card_name TEXT NOT NULL,
    expiry_date DATE NOT NULL,
    cvv TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'blocked', 'expired')),
    credit_limit REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(status);
CREATE INDEX IF NOT EXISTS idx_cards_account_id ON cards(account_id);

-- Create triggers for updated_at timestamps
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_accounts_timestamp 
AFTER UPDATE ON accounts
BEGIN
    UPDATE accounts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- AUDIT LOG TABLE (Phase 2)
-- Tracks every transaction for debugging, compliance, and idempotency
-- ============================================================================

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
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_log(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_idempotency ON audit_log(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_intent ON audit_log(intent);
CREATE INDEX IF NOT EXISTS idx_audit_status ON audit_log(status);

CREATE TRIGGER IF NOT EXISTS update_audit_log_timestamp 
AFTER UPDATE ON audit_log
BEGIN
    UPDATE audit_log SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- SESSIONS TABLE (Phase 2)
-- Stores session state for dialogue continuity
-- ============================================================================

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
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

CREATE TRIGGER IF NOT EXISTS update_sessions_activity 
AFTER UPDATE ON sessions
BEGIN
    UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- IDEMPOTENCY CACHE TABLE (Phase 2)
-- Caches recent requests to detect duplicates
-- ============================================================================

CREATE TABLE IF NOT EXISTS idempotency_cache (
    idempotency_key TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    result_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_idempotency_user ON idempotency_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires ON idempotency_cache(expires_at);

-- Create indexes for better query performance on transactions
CREATE INDEX IF NOT EXISTS idx_txn_idempotency ON transactions(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_txn_audit ON transactions(audit_log_id);
CREATE INDEX IF NOT EXISTS idx_txn_status ON transactions(status);