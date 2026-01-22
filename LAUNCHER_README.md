# Bank Teller Chatbot - Unified Launcher

This directory contains scripts to easily launch both the backend server and Flutter frontend with a single command.

## Quick Start

### Option 1: Batch File (Recommended for Windows)
```bash
# Launch on Windows desktop (default)
run_app.bat

# Launch on web browser
run_app.bat web
```

### Option 2: Python Script
```bash
# Launch on Windows desktop (default)
python launch_app.py

# Launch on web browser
python launch_app.py --device web

# Launch on macOS
python launch_app.py --device macos

# Launch on Linux
python launch_app.py --device linux

# Skip backend startup if already running
python launch_app.py --skip-backend

# Use custom backend port
python launch_app.py --backend-port 8001
```

### Option 3: PowerShell Script
```powershell
# Launch on Windows desktop (default)
.\run_app.ps1

# Launch on web browser
.\run_app.ps1 -device web
```

## What These Scripts Do

1. **Check Backend**: Verifies if the backend server is already running on port 8000
2. **Start Backend**: If not running, automatically launches the FastAPI backend server
3. **Wait for Initialization**: Waits for the backend to be fully ready (~5 seconds)
4. **Launch Flutter**: Starts the Flutter app on the specified device/platform

## Requirements

- **Python 3.10+**: Required for backend
- **Flutter SDK**: Required for frontend
- **Port 8000**: Must be available for backend (or use `--backend-port` flag)

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `netstat -ano | findstr :8000`
- Ensure Python dependencies are installed: `pip install -r backend/requirements.txt`

### Flutter won't launch
- Ensure Flutter is in your PATH: `flutter --version`
- Check connected devices: `flutter devices`
- For web, ensure Chrome/Edge is installed

### Port already in use
- Kill the existing process using port 8000
- Or use a custom port: `python launch_app.py --backend-port 8001`

## Manual Starting (If Scripts Don't Work)

### Terminal 1 - Start Backend
```bash
cd backend/app
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Terminal 2 - Start Flutter
```bash
cd frontend/bank_teller_bot_frontend
flutter run -d windows
# or
flutter run -d web
```

## Available Devices

View all available devices:
```bash
flutter devices
```

Common devices:
- `windows` - Windows Desktop
- `web` - Web Browser (Chrome/Edge)
- `macos` - macOS
- `linux` - Linux Desktop
- `android` - Android Emulator/Device
- `ios` - iOS Simulator/Device

## Architecture

```
┌─────────────────────────────────────┐
│   Launcher Script (run_app.bat)     │
├─────────────────────────────────────┤
│  ├─ Check port 8000                 │
│  ├─ Start Backend (if needed)       │
│  │  └─ FastAPI on 127.0.0.1:8000   │
│  └─ Launch Flutter                  │
│     └─ Connects to Backend API      │
└─────────────────────────────────────┘
```

## API Configuration

The Flutter app is configured to connect to `http://localhost:8000` by default.

See `frontend/bank_teller_bot_frontend/lib/config/app_config.dart` for API settings.
