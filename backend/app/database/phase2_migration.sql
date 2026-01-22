-- Phase 2: Database Schema Updates for Redesign
-- Adds audit logging and transaction management capabilities

-- ============================================================================
-- AUDIT LOG TABLE (NEW)
-- Tracks every transaction for debugging, compliance, and idempotency
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    intent TEXT NOT NULL,
    action TEXT NOT NULL,
    input_data TEXT,  -- JSON serialized input
    output_data TEXT,  -- JSON serialized output
    status TEXT NOT NULL,
    error_message TEXT,
    idempotency_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for audit_log for fast lookups
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_log(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_idempotency ON audit_log(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_intent ON audit_log(intent);
CREATE INDEX IF NOT EXISTS idx_audit_status ON audit_log(status);

-- Trigger to update audit_log timestamp
CREATE TRIGGER IF NOT EXISTS update_audit_log_timestamp 
AFTER UPDATE ON audit_log
BEGIN
    UPDATE audit_log SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- TRANSACTIONS TABLE MODIFICATIONS
-- Adds idempotency and rollback support
-- ============================================================================

-- Add new columns to transactions table (SQLite limitation: one at a time)
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS idempotency_key TEXT UNIQUE;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS audit_log_id INTEGER;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'completed';
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS rollback_data TEXT;

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_txn_idempotency ON transactions(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_txn_audit ON transactions(audit_log_id);
CREATE INDEX IF NOT EXISTS idx_txn_status ON transactions(status);

-- ============================================================================
-- SESSIONS TABLE (NEW - For better session management)
-- Stores session state for dialogue continuity
-- ============================================================================

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,  -- session_id
    user_id INTEGER NOT NULL,
    state_json TEXT,  -- Full dialogue state as JSON
    current_intent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- When session expires
    status TEXT DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

-- Trigger to update last_activity
CREATE TRIGGER IF NOT EXISTS update_sessions_activity 
AFTER UPDATE ON sessions
BEGIN
    UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- IDEMPOTENCY CACHE TABLE (NEW - For duplicate detection cache)
-- Caches recent requests to detect duplicates without DB query
-- ============================================================================

CREATE TABLE IF NOT EXISTS idempotency_cache (
    idempotency_key TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    result_data TEXT,  -- JSON serialized result
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- When cache entry expires (24 hours)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for idempotency_cache
CREATE INDEX IF NOT EXISTS idx_idempotency_user ON idempotency_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires ON idempotency_cache(expires_at);
