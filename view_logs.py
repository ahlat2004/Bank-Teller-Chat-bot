#!/usr/bin/env python3
"""
Log Viewer Utility
Real-time log viewer for Bank Teller Chatbot
Displays logs from both frontend and backend
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import deque

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_log_files():
    """Get all log file paths"""
    project_root = Path(__file__).parent.parent.parent
    logs_dir = project_root / 'logs'
    
    return {
        'backend_main': logs_dir / 'bank_chatbot_backend.log',
        'backend_errors': logs_dir / 'bank_chatbot_errors.log',
        'backend_api': logs_dir / 'bank_chatbot_api.log',
        'frontend': None,  # Frontend logs are in app-specific directory
    }


def read_log_file(filepath, num_lines=None):
    """Read log file and return lines"""
    if not Path(filepath).exists():
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if num_lines:
            return lines[-num_lines:]
        return lines
    except Exception as e:
        return [f"Error reading {filepath}: {e}\n"]


def colorize_log_line(line):
    """Add color to log lines based on level"""
    if 'ERROR' in line or 'CRITICAL' in line:
        return f"{Colors.RED}{line}{Colors.ENDC}"
    elif 'WARNING' in line:
        return f"{Colors.YELLOW}{line}{Colors.ENDC}"
    elif 'INFO' in line:
        return f"{Colors.GREEN}{line}{Colors.ENDC}"
    elif 'DEBUG' in line:
        return f"{Colors.CYAN}{line}{Colors.ENDC}"
    elif 'API' in line:
        return f"{Colors.BLUE}{line}{Colors.ENDC}"
    return line


def display_header(title):
    """Display formatted header"""
    width = 100
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*width}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title.center(width)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*width}{Colors.ENDC}\n")


def view_logs(log_type='all', num_lines=50, follow=False):
    """View logs from files"""
    log_files = get_log_files()
    
    display_header("BANK TELLER CHATBOT - LOG VIEWER")
    
    last_sizes = {}
    
    if follow:
        print(f"{Colors.CYAN}Watching logs... (Press Ctrl+C to stop){Colors.ENDC}\n")
        try:
            while True:
                for name, filepath in log_files.items():
                    if log_type != 'all' and name != log_type:
                        continue
                    
                    if filepath and Path(filepath).exists():
                        current_size = Path(filepath).stat().st_size
                        last_size = last_sizes.get(name, 0)
                        
                        # Only display if file changed
                        if current_size != last_size or name not in last_sizes:
                            print(f"\n{Colors.BOLD}{Colors.CYAN}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {name.upper()}{Colors.ENDC}")
                            print("-" * 100)
                            
                            lines = read_log_file(filepath, num_lines)
                            for line in lines:
                                print(colorize_log_line(line.rstrip()))
                            
                            last_sizes[name] = current_size
                
                time.sleep(2)  # Check every 2 seconds
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Log viewer stopped.{Colors.ENDC}")
    else:
        # Display current logs
        for name, filepath in log_files.items():
            if log_type != 'all' and name != log_type:
                continue
            
            if filepath and Path(filepath).exists():
                print(f"\n{Colors.BOLD}{Colors.CYAN}{name.upper()}{Colors.ENDC}")
                print("-" * 100)
                
                lines = read_log_file(filepath, num_lines)
                for line in lines:
                    print(colorize_log_line(line.rstrip()))
            else:
                print(f"\n{Colors.YELLOW}{name.upper()}: No logs found yet{Colors.ENDC}")


def tail_logs(filepath, num_lines=20):
    """Tail specific log file"""
    display_header(f"TAILING: {Path(filepath).name}")
    
    try:
        while True:
            if Path(filepath).exists():
                lines = read_log_file(filepath)
                
                # Clear screen and display
                os.system('clear' if os.name != 'nt' else 'cls')
                display_header(f"TAILING: {Path(filepath).name}")
                
                for line in lines[-num_lines:]:
                    print(colorize_log_line(line.rstrip()))
                
                print(f"\n{Colors.CYAN}Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tail stopped.{Colors.ENDC}")


def search_logs(pattern, log_type='all'):
    """Search logs for pattern"""
    log_files = get_log_files()
    
    display_header(f"SEARCHING FOR: {pattern}")
    
    total_matches = 0
    
    for name, filepath in log_files.items():
        if log_type != 'all' and name != log_type:
            continue
        
        if filepath and Path(filepath).exists():
            lines = read_log_file(filepath)
            matches = [line for line in lines if pattern.lower() in line.lower()]
            
            if matches:
                print(f"\n{Colors.BOLD}{Colors.CYAN}{name.upper()} ({len(matches)} matches){Colors.ENDC}")
                print("-" * 100)
                
                for match in matches:
                    print(colorize_log_line(match.rstrip()))
                
                total_matches += len(matches)
    
    if total_matches == 0:
        print(f"{Colors.YELLOW}No matches found for '{pattern}'{Colors.ENDC}")
    else:
        print(f"\n{Colors.GREEN}Total matches: {total_matches}{Colors.ENDC}")


def get_log_stats():
    """Display log statistics"""
    log_files = get_log_files()
    
    display_header("LOG STATISTICS")
    
    total_size = 0
    total_lines = 0
    
    for name, filepath in log_files.items():
        if filepath and Path(filepath).exists():
            size = Path(filepath).stat().st_size
            lines = len(read_log_file(filepath))
            
            size_mb = size / (1024 * 1024)
            print(f"{Colors.BOLD}{name.upper()}{Colors.ENDC}")
            print(f"  Size: {size_mb:.2f} MB ({size:,} bytes)")
            print(f"  Lines: {lines:,}")
            print()
            
            total_size += size
            total_lines += lines
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"{Colors.BOLD}TOTAL{Colors.ENDC}")
    print(f"  Size: {total_size_mb:.2f} MB ({total_size:,} bytes)")
    print(f"  Lines: {total_lines:,}")


def main():
    parser = argparse.ArgumentParser(
        description='Log viewer for Bank Teller Chatbot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python view_logs.py                    # View all logs
  python view_logs.py --type backend_api # View API logs only
  python view_logs.py --follow           # Watch logs in real-time
  python view_logs.py --search ERROR     # Search for errors
  python view_logs.py --stats            # Show log statistics
        '''
    )
    
    parser.add_argument('--type', '-t', 
                       choices=['all', 'backend_main', 'backend_errors', 'backend_api'],
                       default='all',
                       help='Type of logs to view (default: all)')
    
    parser.add_argument('--lines', '-n', 
                       type=int, 
                       default=50,
                       help='Number of lines to display (default: 50)')
    
    parser.add_argument('--follow', '-f', 
                       action='store_true',
                       help='Follow log changes in real-time')
    
    parser.add_argument('--search', '-s', 
                       type=str,
                       help='Search logs for pattern')
    
    parser.add_argument('--stats', 
                       action='store_true',
                       help='Display log statistics')
    
    parser.add_argument('--tail', 
                       type=str,
                       help='Tail specific log file')
    
    args = parser.parse_args()
    
    try:
        if args.stats:
            get_log_stats()
        elif args.search:
            search_logs(args.search, args.type)
        elif args.tail:
            tail_logs(args.tail, args.lines)
        else:
            view_logs(args.type, args.lines, args.follow)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == '__main__':
    main()
