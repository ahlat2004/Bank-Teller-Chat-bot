#!/usr/bin/env python3
"""
Bank Teller Chatbot - Integrated App Launcher
Starts backend server and then launches Flutter app
Usage: python launch_app.py [--device windows|web] [--backend-port 8000]
"""

import subprocess
import time
import socket
import sys
import argparse
import os
from pathlib import Path

def is_port_open(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def start_backend(backend_port=8000, timeout=30):
    """Start the backend server"""
    print("\n" + "="*60)
    print("Starting Bank Teller Chatbot Backend")
    print("="*60)
    
    # Get paths
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend" / "app"
    
    # Check if already running
    if is_port_open("127.0.0.1", backend_port):
        print(f"✅ Backend already running on port {backend_port}")
        return True
    
    try:
        print(f"🚀 Starting backend on http://127.0.0.1:{backend_port}...")
        
        # Start backend process
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", 
             "--host", "127.0.0.1", "--port", str(backend_port)],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        
        # Wait for backend to be ready
        print(f"⏳ Waiting for backend to initialize...", end="", flush=True)
        start_time = time.time()
        
        while not is_port_open("127.0.0.1", backend_port):
            if time.time() - start_time > timeout:
                print("\n❌ Backend failed to start within timeout")
                return False
            time.sleep(0.5)
            print(".", end="", flush=True)
        
        print(" ✅")
        print(f"✅ Backend ready at http://127.0.0.1:{backend_port}")
        return True
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def start_flutter(device="windows"):
    """Start Flutter app"""
    print("\n" + "="*60)
    print("Starting Flutter App")
    print("="*60)
    
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend" / "bank_teller_bot_frontend"
    
    try:
        print(f"🚀 Launching Flutter app on {device}...")
        print("")
        
        # Start Flutter
        subprocess.run(
            ["flutter", "run", "-d", device],
            cwd=str(frontend_dir),
            check=False
        )
        
    except Exception as e:
        print(f"❌ Error launching Flutter: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Bank Teller Chatbot - Integrated Launcher"
    )
    parser.add_argument(
        "--device",
        default="windows",
        choices=["windows", "web", "macos", "linux"],
        help="Target device/platform (default: windows)"
    )
    parser.add_argument(
        "--backend-port",
        type=int,
        default=8000,
        help="Backend server port (default: 8000)"
    )
    parser.add_argument(
        "--skip-backend",
        action="store_true",
        help="Skip starting backend (useful if already running)"
    )
    
    args = parser.parse_args()
    
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║   Bank Teller Chatbot - Unified Launcher               ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    # Start backend if not skipped
    if not args.skip_backend:
        if not start_backend(args.backend_port):
            print("⚠️  Backend startup failed, but continuing with Flutter...")
    else:
        print("⏭️  Skipping backend startup (--skip-backend flag set)")
    
    # Start Flutter
    if not start_flutter(args.device):
        sys.exit(1)

if __name__ == "__main__":
    main()
