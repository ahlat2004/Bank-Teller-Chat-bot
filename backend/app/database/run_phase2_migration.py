#!/usr/bin/env python3
"""
Phase 2 Migration Script
Applies database schema changes for audit logging and session management
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_manager import DatabaseManager


def main():
    """Apply Phase 2 migration"""
    print("=" * 80)
    print("Phase 2: Database Schema Migration")
    print("=" * 80)
    print()
    
    # Initialize database manager
    db_path = 'data/bank_demo.db'
    print(f"Applying migration to: {db_path}")
    print()
    
    db = DatabaseManager(db_path)
    
    # Apply migration
    print("📋 Applying Phase 2 migration...")
    success = db.apply_phase2_migration()
    
    if success:
        print()
        print("=" * 80)
        print("✅ Phase 2 Migration Successful!")
        print("=" * 80)
        print()
        print("New tables and columns added:")
        print("  ✅ audit_log table - for transaction auditing")
        print("  ✅ sessions table - for session management")
        print("  ✅ idempotency_cache table - for duplicate detection")
        print("  ✅ transactions.idempotency_key column")
        print("  ✅ transactions.audit_log_id column")
        print("  ✅ transactions.status column")
        print("  ✅ transactions.rollback_data column")
        print()
        print("New methods in db_manager.py:")
        print("  ✅ log_audit() - Log actions to audit_log")
        print("  ✅ get_audit_by_idempotency() - Detect duplicate requests")
        print("  ✅ get_audit_by_user() - Get user's audit trail")
        print("  ✅ get_audit_by_session() - Get session's audit trail")
        print("  ✅ mark_transaction_rolled_back() - Mark transaction as rolled back")
        print("  ✅ create_session() - Create new session")
        print("  ✅ get_session() - Get session by ID")
        print("  ✅ update_session_state() - Update session state")
        print()
        print("Ready for Phase 3: Main Endpoint Refactoring")
        return 0
    else:
        print()
        print("=" * 80)
        print("❌ Phase 2 Migration Failed")
        print("=" * 80)
        print("Check the error messages above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
