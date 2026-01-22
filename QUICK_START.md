# Bank Teller Chatbot - Complete Setup & Launch Guide

## 🚀 Quick Start (One Command)

### Windows Desktop (Recommended)
```bash
run_app.bat
```

### Web Browser
```bash
run_app.bat web
```

### Using Python
```bash
python launch_app.py
```

## 📋 What's Included

### Launcher Scripts
1. **`run_app.bat`** - Windows batch file (Recommended for Windows users)
   - Double-click or run from command prompt
   - Automatically starts backend + Flutter on Windows desktop
   
2. **`run_app.ps1`** - PowerShell script
   - Run with: `.\run_app.ps1` or `.\run_app.ps1 -device web`
   
3. **`launch_app.py`** - Python launcher (Cross-platform)
   - Most flexible and feature-rich
   - Options: `--device`, `--backend-port`, `--skip-backend`
   
4. **`Launch_App_Windows.vbs`** - VBS launcher
   - Double-click to run (Windows only)

## 🔧 System Requirements

✅ **Python 3.10+** - For backend
✅ **Flutter SDK** - For frontend  
✅ **Port 8000** - Available (or use custom port)

## 🏗️ Architecture

```
Your Machine
├── Backend (FastAPI)
│   ├── Port: 8000
│   ├── Host: 127.0.0.1
│   └── Services:
│       ├── Chat API
│       ├── Authentication
│       ├── Balance Check
│       ├── Money Transfer
│       └── Bill Payment
│
└── Frontend (Flutter)
    ├── Platform: Windows/Web/macOS/Linux
    └── Connects to: http://localhost:8000
```

## 📁 Project Structure

```
bank-teller-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py (FastAPI server)
│   │   ├── database/
│   │   ├── auth/
│   │   ├── ml/
│   │   └── utils/
│   └── requirements.txt
│
├── frontend/
│   └── bank_teller_bot_frontend/
│       ├── lib/
│       │   ├── config/
│       │   ├── services/
│       │   ├── providers/
│       │   ├── screens/
│       │   └── widgets/
│       ├── pubspec.yaml
│       └── flutter build files
│
├── data/
│   ├── models/ (ML models)
│   └── processed/ (datasets)
│
└── Launcher Scripts (NEW!)
    ├── run_app.bat
    ├── run_app.ps1
    ├── launch_app.py
    └── Launch_App_Windows.vbs
```

## 🎯 How the Launcher Works

### Step 1: Check Backend
- Checks if port 8000 is already in use
- If yes → uses existing backend
- If no → starts new backend

### Step 2: Start Backend (if needed)
- Launches FastAPI server in a separate window
- Loads all ML models and components
- Waits for full initialization (~8 seconds)

### Step 3: Launch Flutter
- Starts Flutter app on selected device/platform
- App automatically connects to backend API
- Ready to use!

## 🌐 Supported Platforms

Run on any of these with the launcher:

```bash
# Windows Desktop
run_app.bat
# or
python launch_app.py --device windows

# Web Browser
run_app.bat web
# or
python launch_app.py --device web

# macOS
python launch_app.py --device macos

# Linux
python launch_app.py --device linux

# Android Emulator
python launch_app.py --device android-emulator

# iOS Simulator
python launch_app.py --device ios-simulator
```

## 🛠️ Advanced Options

### Using Python Launcher with Options

```bash
# Skip backend if already running
python launch_app.py --skip-backend

# Use custom backend port
python launch_app.py --backend-port 8001

# Combine options
python launch_app.py --device web --backend-port 8001 --skip-backend
```

## 🐛 Troubleshooting

### Backend Won't Start

**Problem**: "Port 8000 already in use"
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use custom port
python launch_app.py --backend-port 8001
```

**Problem**: "Python not found"
- Ensure Python 3.10+ is installed
- Check: `python --version`
- Add Python to PATH if needed

### Flutter Won't Launch

**Problem**: "Flutter command not found"
- Ensure Flutter SDK is installed
- Check: `flutter --version`
- Add Flutter to PATH if needed

**Problem**: "No connected devices"
```bash
# List available devices
flutter devices

# For web, ensure Chrome/Edge is installed
# For mobile, connect device or start emulator
```

### API Connection Issues

**Problem**: "Cannot connect to backend"
- Verify backend is running: `http://localhost:8000/health`
- Check firewall isn't blocking port 8000
- Ensure Flutter app config has correct URL (lib/config/app_config.dart)

## 📊 API Endpoints Available

```
POST   /api/chat              - Chat with the bot
GET    /api/balance/{user_id} - Check account balance
POST   /api/transfer          - Transfer money
POST   /api/bill-payment      - Pay bills
POST   /api/auth/send-otp     - Send OTP
POST   /api/auth/verify-otp   - Verify OTP
GET    /health                - Health check
```

## 🔒 Security Notes

⚠️ **Development Only**
- Backend runs on `127.0.0.1` (localhost) - not accessible from network
- CORS is set to allow all origins
- Use real authentication and HTTPS in production

## 📝 Manual Steps (If Launcher Doesn't Work)

### Terminal 1: Start Backend
```bash
cd backend/app
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Terminal 2: Start Flutter
```bash
cd frontend/bank_teller_bot_frontend
flutter run -d windows
```

## 💡 Tips

1. **Keep Backend Running**: Don't close the backend window while using the app
2. **Multiple Instances**: You can run launcher multiple times with different platforms
3. **Hot Reload**: In Flutter, press 'r' for hot reload, 'R' for full restart
4. **Debug**: Check backend server.log for API errors
5. **Logs**: Flutter console shows detailed logs when running

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flutter Documentation](https://flutter.dev/docs)
- [Dio HTTP Client](https://pub.dev/packages/dio)
- [Provider State Management](https://pub.dev/packages/provider)

## 📞 Support

If issues persist:
1. Check the troubleshooting section above
2. Review LAUNCHER_README.md for more details
3. Check backend server.log for error messages
4. Ensure all dependencies are installed:
   - Backend: `pip install -r backend/requirements.txt`
   - Frontend: `cd frontend/bank_teller_bot_frontend && flutter pub get`

---

**Happy Coding! 🚀**

The app is now ready to use with a single command!
