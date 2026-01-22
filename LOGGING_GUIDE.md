# Bank Teller Chatbot - Comprehensive Logging Guide

## Overview

The application now features complete end-to-end logging that captures everything from the Flutter frontend all the way through to the Python backend. All logs are automatically saved to files for troubleshooting and debugging.

---

## Log Files Location

### Backend Logs
Located in: `<PROJECT_ROOT>/logs/`

- **bank_chatbot_backend.log** - Main backend log (all levels)
- **bank_chatbot_errors.log** - Error logs only
- **bank_chatbot_api.log** - API request/response logs

### Frontend Logs
Located in:
- **Windows**: `C:\Users\<username>\AppData\Local\BankTellerChatbot\logs\`
- **macOS/Linux**: `~/.config/BankTellerChatbot/logs/`

- **bank_chatbot_app.log** - Main frontend application log

---

## What Gets Logged

### Frontend Logging (Flutter)

#### Application Level
- ✅ Application startup/shutdown
- ✅ Storage initialization
- ✅ Chat provider initialization
- ✅ Session creation and management

#### User Interactions
- ✅ User sending chat messages
- ✅ Message timestamps and IDs
- ✅ User balance fetch requests
- ✅ Account creation attempts

#### API Communication
- ✅ All API requests (method, endpoint, data)
- ✅ API responses (status, data length)
- ✅ API errors (type, message, stack trace)
- ✅ Timeout/connection errors
- ✅ Request/response timing

#### Data Management
- ✅ Message saving/loading
- ✅ Session persistence
- ✅ Storage operations
- ✅ User ID updates

### Backend Logging (Python)

#### Server Events
- ✅ Server startup/shutdown
- ✅ Component initialization (database, ML models, etc.)
- ✅ Uvicorn server events
- ✅ Model loading and artifact status

#### API Endpoints
- ✅ All incoming API requests
- ✅ Request parameters
- ✅ Response status codes
- ✅ Error responses with details

#### Database Operations
- ✅ Database connections
- ✅ Query execution
- ✅ Transaction management
- ✅ Error handling

#### Machine Learning
- ✅ Intent classification results
- ✅ Confidence scores
- ✅ Entity extraction results
- ✅ Model inference timing

#### Business Logic
- ✅ Dialogue state changes
- ✅ Session management
- ✅ Authentication operations
- ✅ Transaction processing

---

## How Logging Works

### Logging Levels

```
DEBUG   - Detailed diagnostic information
INFO    - General informational messages
WARNING - Warning messages for potentially problematic situations
ERROR   - Error messages for failed operations
CRITICAL- Critical errors requiring immediate attention
```

### Log Format

#### Frontend Logs
```
2025-12-07 16:30:45.123 [INFO] [ChatProvider] Sending user message | {messageLength=45, sessionId=abc123}
2025-12-07 16:30:46.456 [DEBUG] [ApiService] API Request | {method=POST, path=/api/chat, baseUrl=http://127.0.0.1:8000}
2025-12-07 16:30:47.789 [INFO] [ApiService] API Response | {statusCode=200, path=/api/chat, contentLength=250}
```

#### Backend Logs
```
2025-12-07 16:30:47 - bank_teller_chatbot - INFO - [main.py:95] - Chat request received: user_id=1, intent=check_balance
2025-12-07 16:30:47 - bank_teller_chatbot - DEBUG - [dialogue_manager.py:45] - Processing intent with confidence: 0.92
2025-12-07 16:30:48 - bank_teller_chatbot - INFO - [main.py:110] - Chat response sent: status=success
```

---

## Viewing Logs

### Method 1: Using the Log Viewer Tool

```powershell
# View all logs
python view_logs.py

# View only backend API logs
python view_logs.py --type backend_api

# View last 100 lines
python view_logs.py --lines 100

# Follow logs in real-time
python view_logs.py --follow

# Search for errors
python view_logs.py --search ERROR

# Show log statistics
python view_logs.py --stats
```

### Method 2: Direct File Viewing

**Windows:**
```powershell
# View backend log
Get-Content logs\bank_chatbot_backend.log -Tail 50

# Search for errors
Select-String "ERROR" logs\bank_chatbot_*.log
```

**macOS/Linux:**
```bash
# Tail backend log
tail -f logs/bank_chatbot_backend.log

# Search for errors
grep "ERROR" logs/bank_chatbot_*.log
```

### Method 3: Text Editor

Simply open the log files directly:
- `logs/bank_chatbot_backend.log`
- `logs/bank_chatbot_api.log`
- `logs/bank_chatbot_errors.log`

---

## Troubleshooting Guide

### Issue: Application Crashes

1. **Check Frontend Logs**
   ```powershell
   python view_logs.py --type frontend --search CRITICAL
   ```

2. **Check Backend Logs**
   ```powershell
   python view_logs.py --type backend_errors
   ```

3. **Look for Stack Traces**
   - Frontend logs will show full stack trace with line numbers
   - Backend logs will include exception details

### Issue: API Connection Failures

1. **Check API Logs**
   ```powershell
   python view_logs.py --type backend_api --follow
   ```

2. **Search for Connection Errors**
   ```powershell
   python view_logs.py --search "Connection"
   ```

3. **Check Timeout Issues**
   ```powershell
   python view_logs.py --search "timeout"
   ```

### Issue: Slow Performance

1. **Check Response Times**
   ```powershell
   python view_logs.py --type backend_api
   ```

2. **Monitor in Real-Time**
   ```powershell
   python view_logs.py --follow
   ```

### Issue: Model/ML Errors

1. **Check Model Loading**
   ```powershell
   python view_logs.py --search "intent classifier"
   ```

2. **Check Inference Results**
   ```powershell
   python view_logs.py --search "confidence"
   ```

### Issue: Database Errors

1. **Search for DB Operations**
   ```powershell
   python view_logs.py --search "DATABASE"
   ```

2. **Check Transaction Logs**
   ```powershell
   python view_logs.py --search "transaction"
   ```

---

## Log Rotation

### Automatic Log Rotation

- **Frontend**: Logs are rotated when file reaches 5MB
- **Backend**: Logs are managed by logging module
- **Old logs**: Automatically backed up with timestamp

### Manual Log Cleanup

```powershell
# Remove logs older than 7 days
Remove-Item logs\*.log -Force -ErrorAction SilentlyContinue

# Archive current logs
Move-Item logs\bank_chatbot_*.log "logs\archive\$(Get-Date -Format 'yyyyMMdd_HHmmss')_logs.zip"
```

---

## Integration with Launchers

### Automatic Logging on Startup

When you run the application using any launcher:

```powershell
.\run_app.bat
```

The following happens automatically:
1. ✅ Logging service initializes in frontend
2. ✅ Backend logging is configured
3. ✅ Log files are created
4. ✅ All operations are logged
5. ✅ Logs persist until application closes

### View Logs After Running

```powershell
# After running the app, view logs
python view_logs.py --follow

# Or search for specific issues
python view_logs.py --search "ERROR"
```

---

## Best Practices

### 1. Regular Log Review
- Check logs after any errors
- Review API logs for performance issues
- Monitor for warnings

### 2. Log Archiving
- Archive old logs before they get too large
- Keep important logs for reference
- Organize by date

### 3. Debugging Workflow
```
1. Run app with: run_app.bat
2. Reproduce the issue
3. Check logs with: python view_logs.py --follow
4. Search for errors: python view_logs.py --search ERROR
5. Review stack traces for details
6. Fix issues
7. Test again
```

### 4. Performance Monitoring
- Use real-time log watching for performance
- Check API response times
- Monitor database operations
- Watch for warnings

---

## Log Retention Policy

| Log Type | Retention | Size Limit | Archive |
|----------|-----------|-----------|---------|
| Backend Main | 30 days | 10 MB | Yes |
| Backend API | 7 days | 5 MB | Yes |
| Backend Errors | 30 days | 10 MB | Yes |
| Frontend | 14 days | 5 MB | Yes |

---

## Configuration

### Change Log Levels

**Frontend** (`lib/services/logging_service.dart`):
```dart
static const LogLevel defaultLevel = LogLevel.debug;
```

**Backend** (`app/utils/logging_config.py`):
```python
root_logger.setLevel(logging.DEBUG)  # Change to INFO, WARNING, etc.
```

### Change Log Locations

**Frontend**:
Modify `_getLogDirectory()` in `logging_service.dart`

**Backend**:
Modify `LOG_DIR` in `logging_config.py`

---

## Troubleshooting Commands

```powershell
# Quick status check
python view_logs.py --stats

# Monitor everything in real-time
python view_logs.py --follow

# Find all errors
python view_logs.py --search ERROR

# Find all API issues
python view_logs.py --type backend_api --search "Error\|ERROR\|failed"

# Get recent activity
python view_logs.py --lines 200

# Search for connection issues
python view_logs.py --search "Connection\|timeout\|refused"

# Check model loading
python view_logs.py --search "classifier\|model\|Loading"
```

---

## Support

If you encounter issues:

1. **Collect Logs**
   ```powershell
   python view_logs.py > diagnostic_logs.txt
   ```

2. **Search for Errors**
   ```powershell
   python view_logs.py --search ERROR > errors.txt
   ```

3. **Review Stack Traces**
   - Look for exception details
   - Check line numbers
   - Note the source (frontend or backend)

4. **Share Diagnostic Information**
   - Provide error logs
   - Include relevant stack traces
   - Note when error occurred
   - Describe what you were doing

---

## Summary

✅ **Comprehensive Logging**: Every action is logged
✅ **Automatic File Management**: Logs are automatically created and managed
✅ **Easy Viewing**: Multiple ways to view and search logs
✅ **Real-time Monitoring**: Watch logs as they happen
✅ **Debugging Support**: Full stack traces and detailed error info
✅ **Performance Tracking**: Monitor API and database performance

The logging system is designed to help you quickly identify and fix any issues that arise!
