-- Authentication Tables Schema
-- OTP and verification system
-- Place in: backend/app/database/schema_auth.sql

-- OTP Sessions Table
CREATE TABLE IF NOT EXISTS otp_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    purpose TEXT NOT NULL CHECK(purpose IN ('account_creation', 'transaction', 'login')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3
);

-- Verified Sessions Table  
CREATE TABLE IF NOT EXISTS verified_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    user_id INTEGER,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    purpose TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_otp_email_purpose ON otp_sessions(email, purpose);
CREATE INDEX IF NOT EXISTS idx_otp_created_at ON otp_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_verified_sessions_email ON verified_sessions(email);
CREATE INDEX IF NOT EXISTS idx_verified_sessions_user_id ON verified_sessions(user_id);

-- Cleanup trigger for old OTP sessions (auto-delete after 24 hours)
CREATE TRIGGER IF NOT EXISTS cleanup_old_otp_sessions
AFTER INSERT ON otp_sessions
BEGIN
    DELETE FROM otp_sessions
    WHERE created_at < datetime('now', '-24 hours');
END;