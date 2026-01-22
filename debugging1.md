# Bank Teller Chatbot — Debugging Handover (debugging1.md)

Date: 2025-12-08

Purpose
- A concise handover and troubleshooting summary of the recent debugging session that focused on session persistence and OTP/email verification.

1) High-level summary
- Root problem discovered: sessions were not persisting between requests in some runs — state.intent was becoming None because `session_manager.get_session()` returned None in production-like runs.
- Work performed: added debug tracing, centralized response helper, fixed many early-return responses to include debug fields, added a "force fresh" startup option, added session clearing helper, created a test harness for OTP sending, and iterated on email sending configuration.

2) New files created
- `send_otp_test.py` — project-root script to trigger an OTP send via `AuthManager` (defaults to `apexwolf993@gmail.com`, accepts CLI override). Kept test recipient out of backend.

3) Files edited (major changes)
- `backend/app/main.py`
  - Added `make_response()` helper to ensure all responses consistently include the debug fields: `debug_state_intent` and `debug_session_found`.
  - Initialized `session_found` early and ensured main/early returns use `make_response` or JSONResponse with `exclude_none=False` so debug fields are always present in responses.
  - Wired `FORCE_FRESH_SESSIONS` environment variable to call `session_manager.clear_all_sessions()` at startup when enabled.
  - Replaced many ad-hoc `ChatResponse(...)` returns with the centralized `make_response(...)` to include debug data.

- `backend/app/utils/session_manager.py`
  - Added `clear_all_sessions()` to clear in-memory sessions (returns count cleared).
  - Replaced `print()` cleanup messages with logger calls.

- `backend/app/auth/email_service.py`
  - Added fallback defaults for SMTP credentials (temporarily used for quick testing). NOTE: credentials were added inline for testing only — this is insecure and should be reverted.
  - Email formatting (HTML + text) left intact; sends via Gmail SMTP by default.

- `send_otp_test.py` (new)
  - CLI script to trigger OTP send using `AuthManager.initiate_email_verification()`; default recipient is `apexwolf993@gmail.com` but can be overridden on CLI.

- `test_debug_intent.py` (modified)
  - Added printing of `debug_state_intent` and `debug_session_found` so test shows whether session was found and what state.intent is.

4) Fixes implemented
- Centralized response generation via `make_response()` so debug fields are always included in API responses (helps trace session persistence issues).
- Ensured `session_found` is initialized and set reliably in the chat flow.
- Added `SessionManager.clear_all_sessions()` and startup handling for `FORCE_FRESH_SESSIONS` — allows starting with a fresh in-memory session store while preserving the DB seed data.

5) Tests performed and results
- `test_debug_intent.py` (focused): showed that when server started with `FORCE_FRESH_SESSIONS=1`, sessions persist during the run and `state.intent` is preserved across MSG1/MSG2. Example output observed:
  - MSG1 - Intent: create_account, State Intent: create_account, Session Found: True
  - MSG2 - Intent: create_account, State Intent: create_account, Session Found: True

- `comprehensive_customer_test.py` (full end-to-end):
  - Initial run (with earlier setup) produced 11/12 passing (92%) where the failing test was email verification.
  - After attempting to test with in-file SMTP creds, a later run produced 10/12 passing; the account email verification step failed due to SMTP auth.

6) Current known issues / root cause summary
- The OTP generation path is working (OTP created and logged). The email sending fails due to SMTP authentication failure:
  - Logs show: `Failed to send OTP email: (535, b'5.7.8 Username and Password not accepted ... BadCredentials ... - gsmtp')`
  - This is a Gmail credential/authentication issue (bad app password, account blocked, or whitespace/typo in credentials).
- The session persistence bug (where sessions were previously not found and fresh DialogueState was created every request) appears to be mitigated when running the server with a fresh in-memory session manager and the recent code fixes; however, persistence across separate server runs is by design not present (sessions are in-memory only). If the app was observed 'losing' sessions across runs previously, that was likely caused by starting a new process/instance (expected) or by multiple SessionManager instances being used incorrectly — code now initializes a global `session_manager` on startup.

7) How to reproduce (quick)
- Start server fresh (recommended via `run_app.bat`) with the `FORCE_FRESH_SESSIONS` env var to ensure clean session store:
  - PowerShell (temporary var):
    ```powershell
    $env:FORCE_FRESH_SESSIONS = '1'
    .\run_app.bat windows
    ```
- Run the debug test:
  - `python test_debug_intent.py`
- Run the OTP test (after configuring SMTP):
  - `python send_otp_test.py apexwolf993@gmail.com`

8) Where to look for logs
- Backend logs (tail these while reproducing): `backend/logs/bank_chatbot_backend.log`
- API logs (requests): `backend/logs/bank_chatbot_api.log`
- Error logs: `backend/logs/bank_chatbot_errors.log`

9) Immediate remediation steps for SMTP failure
- Do NOT keep credentials in source. Instead set these environment variables when running the server:
  - `SMTP_EMAIL` — the Gmail address used to send OTP emails
  - `SMTP_PASSWORD` — the Gmail App Password (no spaces) created under the account's security settings
- If Gmail returns `535 BadCredentials`:
  - Recreate an App Password (Google account must have 2FA enabled), copy it exactly (no spaces), and set it in `SMTP_PASSWORD`.
  - Check the account security email for blocked sign-in attempts and allow access if required.

10) Security & housekeeping notes
- I temporarily added hard-coded SMTP defaults in `backend/app/auth/email_service.py` to speed testing. Remove these before committing or sharing the repo.
- Consider adding an `EMAIL_TEST_MODE` env var to mock sending in CI/test runs instead of hitting external SMTP.

11) Suggested next actions (recommended ordering)
1. Replace the hardcoded SMTP credentials with environment variables and restart the server. Verify a single OTP send to a real recipient (use `send_otp_test.py`).
2. If immediate external email sending is not possible, add a temporary `EMAIL_TEST_MODE` to skip SMTP and log OTPs for acceptance tests.
3. Run `python comprehensive_customer_test.py` after SMTP is confirmed or mock is enabled and verify 12/12 tests pass.
4. Remove temporary debug additions (if any), and revert hardcoded creds.

12) Useful commands (PowerShell)
- Clear compiled Python caches (keeps DB):
  ```powershell
  Get-ChildItem -Path . -Recurse -Include "__pycache__","*.pyc" | ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
  ```
- Start server with fresh sessions:
  ```powershell
  $env:FORCE_FRESH_SESSIONS='1'
  .\run_app.bat windows
  ```
- Run OTP test:
  ```powershell
  python send_otp_test.py apexwolf993@gmail.com
  ```

13) Contact / Handover notes
- The main touch points for future debugging are:
  - `backend/app/main.py` — chat endpoint orchestration, session handling, response generation
  - `backend/app/utils/session_manager.py` — in-memory session store
  - `backend/app/auth/email_service.py` & `backend/app/auth/auth_manager.py` — OTP and email flow
  - `send_otp_test.py` — test harness for OTPs

If you want, I can now:
- Revert the hardcoded SMTP credentials and switch to using only env vars, or
- Add `EMAIL_TEST_MODE` so tests don't require real SMTP, or
- Run the focused OTP send now (if you confirmed SMTP creds are valid).

-- End of handover
