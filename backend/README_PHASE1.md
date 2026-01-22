# Phase 1: Email OTP System - Implementation Guide

## 🎯 Overview

Phase 1 adds **email-based OTP verification** to your chatbot for:
- ✅ Account creation (secure registration)
- ✅ High-value transactions (>PKR 25,000)
- ✅ Future login system

---

## 📁 File Structure

Create these new files:

```
backend/app/
├── auth/                          ← NEW FOLDER
│   ├── __init__.py               ← NEW
│   ├── email_service.py          ← NEW (Sends OTP emails)
│   ├── otp_manager.py            ← NEW (Generates/validates OTPs)
│   └── auth_manager.py           ← NEW (Orchestrates auth)
│
└── database/
    └── schema_auth.sql           ← NEW (Auth tables)
```

Update these existing files:
```
backend/app/
├── database/
│   └── db_manager.py             ← ADD auth methods
│
├── models/
│   └── dialogue_manager.py       ← ADD OTP slots
│
└── main.py                       ← ADD auth endpoints
```

---

## 🔧 Installation Steps

### Step 1: Create New Files

Copy all 5 new files to their locations:

1. `backend/app/auth/__init__.py`
2. `backend/app/auth/email_service.py`
3. `backend/app/auth/otp_manager.py`
4. `backend/app/auth/auth_manager.py`
5. `backend/app/database/schema_auth.sql`

### Step 2: Update Existing Files

**A. Update `db_manager.py`:**
- Add `check_email_exists()` method
- Add `initialize_auth_tables()` method
- Add `_create_auth_tables_inline()` method
- Call `initialize_auth_tables()` in `__init__`

**B. Update `dialogue_manager.py`:**
- Add `'otp_code'` to `intent_slots` for create_account
- Add prompts for: `name`, `phone`, `email`, `otp_code`
- Update `_fill_slots_from_entities()` to handle new slots

**C. Update `main.py`:**
- Import `AuthManager`
- Add global `auth_manager` variable
- Initialize in `startup_event()`
- Update `/api/chat` endpoint for OTP handling
- Add `handle_otp_resend()` function
- Update `execute_action()` for create_account with OTP
- Add 3 new endpoints: `/api/auth/send-otp`, `/api/auth/verify-otp`, `/api/auth/check-email`

---

## 📧 Email Configuration

### Option 1: Gmail (Recommended)

1. **Enable 2-Factor Authentication:**
   - Go to: https://myaccount.google.com/security
   - Enable 2FA

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Set Environment Variables:**

**Linux/Mac:**
```bash
export SMTP_EMAIL='your-email@gmail.com'
export SMTP_PASSWORD='your-16-char-app-password'
```

**Windows (PowerShell):**
```powershell
$env:SMTP_EMAIL='your-email@gmail.com'
$env:SMTP_PASSWORD='your-16-char-app-password'
```

**Or create `.env` file:**
```
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
```

### Option 2: Other SMTP Providers

Update `email_service.py` with your provider's settings:
```python
self.smtp_host = 'smtp.yourprovider.com'
self.smtp_port = 587  # or 465 for SSL
```

---

## 🧪 Testing

### Test 1: Run Setup Script

```bash
python setup_phase1.py
```

This will:
- ✅ Verify file structure
- ✅ Initialize database tables
- ✅ Test OTP generation
- ✅ Test email sending (optional)

### Test 2: Test OTP Manager Standalone

```bash
cd backend/app
python auth/otp_manager.py
```

Expected output:
```
✅ OTP created for test@example.com: 123456
✅ OTP verified successfully!
```

### Test 3: Test Email Service

```bash
cd backend/app
python auth/email_service.py
```

Follow prompts to send test email.

### Test 4: Full Integration Test

1. **Start server:**
```bash
uvicorn backend.app.main:app --reload
```

2. **Test account creation:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "I want to create a new account",
    "user_id": 1
  }'
```

3. **Follow the conversation:**
```
Bot: "What's your name?"
You: "Ahmed Ali"

Bot: "What's your phone number?"
You: "03001234567"

Bot: "What's your email?"
You: "ahmed.ali@gmail.com"

Bot: "✉️ Verification code sent to ahmed.ali@gmail.com..."
[Check your email for OTP]

You: "123456"  (your OTP)

Bot: "✅ Email verified! What type of account?"
You: "savings"

Bot: "Please confirm..."
You: "yes"

Bot: "🎉 Account created! Account Number: PK56NEWB..."
```

---

## 🔒 Security Features

### OTP Security:
- ✅ 6-digit random code
- ✅ 5-minute expiry
- ✅ Max 3 attempts
- ✅ One-time use only

### Email Security:
- ✅ Duplicate email detection
- ✅ Verification before account creation
- ✅ Secure SMTP with TLS

### Session Security:
- ✅ OTPs stored in database (not in memory)
- ✅ Automatic cleanup of expired sessions
- ✅ Verification status tracked

---

## 📊 Database Tables

Two new tables added:

### `otp_sessions`
```sql
id              INTEGER PRIMARY KEY
email           TEXT NOT NULL
otp_code        TEXT NOT NULL
purpose         TEXT (account_creation/transaction/login)
created_at      TIMESTAMP
expires_at      TIMESTAMP
verified        BOOLEAN
attempts        INTEGER
max_attempts    INTEGER
```

### `verified_sessions`
```sql
id              INTEGER PRIMARY KEY
session_id      TEXT UNIQUE
email           TEXT
user_id         INTEGER
verified_at     TIMESTAMP
expires_at      TIMESTAMP
purpose         TEXT
```

---

## 🎯 User Flow

### Account Creation with OTP:

```
┌─────────────────────┐
│ User: Create account│
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Bot: What's name?   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ User: Ahmed Ali     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Bot: Phone number?  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ User: 03001234567   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Bot: Email?         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ User: ahmed@email   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Check if exists     │
│ Generate OTP        │
│ Send email          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Bot: Code sent!     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ User: 123456        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Verify OTP          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ ✅ Email verified   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Bot: Account type?  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ User: savings       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Bot: Confirm?       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ User: yes           │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Create user + acc   │
│ Send welcome email  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 🎉 Account created! │
└─────────────────────┘
```

---

## 🐛 Troubleshooting

### Issue: "Failed to send email"

**Solution:**
- Verify SMTP credentials are set
- Check Gmail app password is correct
- Ensure 2FA is enabled on Gmail
- Try different port (587 or 465)

### Issue: "OTP not found"

**Solution:**
- OTPs expire in 5 minutes
- Request new OTP by typing "resend"
- Check email was entered correctly

### Issue: "Email already exists"

**Solution:**
- This is intentional - prevents duplicate accounts
- User should use existing account or contact support

### Issue: "Database error: no such table otp_sessions"

**Solution:**
```bash
python setup_phase1.py
```
This will create the tables.

---

## 📝 API Endpoints

### New Endpoints:

**1. Send OTP**
```
POST /api/auth/send-otp
Body: { "email": "user@email.com", "purpose": "account_creation" }
Response: { "success": true, "message": "..." }
```

**2. Verify OTP**
```
POST /api/auth/verify-otp
Body: { "email": "user@email.com", "otp_code": "123456", "purpose": "account_creation" }
Response: { "success": true, "message": "..." }
```

**3. Check Email**
```
GET /api/auth/check-email/{email}
Response: { "exists": true/false }
```

---

## ✅ Phase 1 Checklist

Before moving to Phase 2:

- [ ] All 5 new files created
- [ ] 3 existing files updated
- [ ] Database tables initialized
- [ ] SMTP credentials configured
- [ ] Test OTP generation works
- [ ] Test email sending works
- [ ] Full account creation tested
- [ ] Welcome email received
- [ ] No errors in logs

---

## 🚀 What's Next?

**Phase 2: Transaction Receipts & Error Handling**
- Text receipts for transactions
- JSON receipts for frontend
- Enhanced error messages
- Better input validation

---

## 💡 Tips

1. **Use Test Mode:** During development, you can bypass OTP by checking a test flag
2. **Monitor Emails:** Check spam folder if emails not received
3. **Rate Limiting:** Consider adding rate limits to prevent OTP spam
4. **Logging:** All OTP operations are logged for debugging

---

## 📞 Support

If you encounter issues:
1. Check logs: `tail -f backend.log`
2. Verify environment variables: `echo $SMTP_EMAIL`
3. Test components individually before integration
4. Check database: `sqlite3 data/bank_demo.db "SELECT * FROM otp_sessions;"`

---

**Phase 1 Complete!** 🎉

Your chatbot now has secure email OTP verification for account creation!