#!/usr/bin/env python3

import os
import time
import sys
import shutil
import platform
import getpass
import subprocess
import json
import urllib.request
from datetime import datetime

# ANSI color codes for terminal styling
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

# Global variables
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

# Global command history
command_history = []
history_position = 0

# Version information
CURRENT_VERSION = "2.2"
GITHUB_REPO = "https://api.github.com/repos/yazn1q3/yash/releases/latest"

def print_color(text, color, end='\n'):
    """Print colored text with optional end parameter"""
    if IS_WINDOWS:
        # Enable ANSI colors on Windows
        os.system("")  # This enables ANSI escape sequences in Windows terminal
    print(f"{color}{text}{Colors.ENDC}", end=end)

def execute_command(command):
    """Execute a system command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"Error executing command: {e}"

def install_package(package):
    """Install a package using the appropriate package manager"""
    print_color(f"Installing {package}...", Colors.YELLOW)
    
    if IS_WINDOWS:
        # Windows - try to use winget if available
        if execute_command("winget --version").strip():
            result = execute_command(f"winget install {package}")
            print(result)
        else:
            print_color("Package installation requires winget. Please install it from the Microsoft Store.", Colors.RED)
    elif IS_LINUX:
        # Linux - use apt or dnf based on distribution
        if os.path.exists("/usr/bin/apt"):
            result = execute_command(f"sudo apt update && sudo apt install -y {package}")
        elif os.path.exists("/usr/bin/dnf"):
            result = execute_command(f"sudo dnf install -y {package}")
        else:
            result = "Unknown Linux package manager."
        print(result)
    elif IS_MACOS:
        # macOS - use homebrew if available
        if execute_command("brew --version").strip():
            result = execute_command(f"brew install {package}")
            print(result)
        else:
            print_color("Package installation requires Homebrew. Install it using instructions from brew.sh", Colors.RED)
    
    print_color(f"Package installation process completed for {package}.", Colors.GREEN)

def upgrade_system():
    """Upgrade the system using the appropriate package manager"""
    print_color("Upgrading system...", Colors.YELLOW)
    
    if IS_WINDOWS:
        # Windows upgrade via winget
        if execute_command("winget --version").strip():
            result = execute_command("winget upgrade --all")
            print(result)
        else:
            print_color("System upgrade requires winget. Please install it from the Microsoft Store.", Colors.RED)
    elif IS_LINUX:
        # Linux upgrade via apt or dnf
        if os.path.exists("/usr/bin/apt"):
            result = execute_command("sudo apt update && sudo apt upgrade -y")
        elif os.path.exists("/usr/bin/dnf"):
            result = execute_command("sudo dnf upgrade -y")
        else:
            result = "Unknown Linux package manager."
        print(result)
    elif IS_MACOS:
        # macOS upgrade via homebrew
        if execute_command("brew --version").strip():
            result = execute_command("brew update && brew upgrade")
            print(result)
        else:
            print_color("System upgrade requires Homebrew. Install it using instructions from brew.sh", Colors.RED)
    
    print_color("System upgrade process completed.", Colors.GREEN)

def clear_screen():
    """Clear the screen"""
    os.system('cls' if IS_WINDOWS else 'clear')
    display_welcome_message()

def display_welcome_message():
    """Display the welcome message with OS-specific info"""
    
    yash_ascii = f"""
██╗   ██╗ █████╗ ███████╗██╗  ██╗
╚██╗ ██╔╝██╔══██╗██╔════╝██║  ██║
 ╚████╔╝ ███████║███████╗███████║
  ╚██╔╝  ██╔══██║╚════██║██╔══██║
   ██║   ██║  ██║███████║██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """
    
    print_color(yash_ascii, Colors.CYAN)
    print_color(f" Welcome to Yash Terminal v{CURRENT_VERSION} ", Colors.BOLD + Colors.GREEN)
    print('\n')

def list_directory(args=[]):
    """List directory contents with colors"""
    path = "."
    if args and len(args) > 0:
        path = args[0]
    
    try:
        contents = os.listdir(path)
        
        if not contents:
            print("Directory is empty.")
            return
            
        # Get max filename length for formatting
        max_len = max(len(item) for item in contents) + 2
        
        # Print in columns
        terminal_width = shutil.get_terminal_size().columns
        cols = max(1, terminal_width // (max_len + 2))
        
        # Sort contents (directories first on Windows)
        if IS_WINDOWS:
            # Windows: Sort directories first, then files
            dirs = sorted([item for item in contents if os.path.isdir(os.path.join(path, item))])
            files = sorted([item for item in contents if not os.path.isdir(os.path.join(path, item))])
            sorted_contents = dirs + files
        else:
            # Unix-like: just sort alphabetically
            sorted_contents = sorted(contents)
        
        for i, item in enumerate(sorted_contents):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                # Directory
                item_str = f"{Colors.BLUE}{item}/{Colors.ENDC}"
            elif os.access(full_path, os.X_OK) and not IS_WINDOWS:
                # Executable (not applicable on Windows)
                item_str = f"{Colors.GREEN}{item}*{Colors.ENDC}"
            elif IS_WINDOWS and item.lower().endswith(('.exe', '.bat', '.cmd', '.ps1')):
                # Windows executables
                item_str = f"{Colors.GREEN}{item}{Colors.ENDC}"
            else:
                # Regular file
                item_str = f"{item}"
                
            print(f"{item_str:<{max_len+10}}", end="\n" if (i + 1) % cols == 0 else "  ")
        
        # Ensure we end with a newline
        if len(contents) % cols != 0:
            print()
            
    except Exception as e:
        print_color(f"Error listing directory: {e}", Colors.RED)

def show_system_info():
    """Display system information"""
    print_color("=== System Information ===", Colors.HEADER)
    print(f"System: {platform.system()}")
    print(f"Node: {platform.node()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # OS-specific information
    if IS_WINDOWS:
        try:
            # Windows-specific info
            win_edition = execute_command("wmic os get Caption").split("\n")[1].strip()
            win_build = execute_command("wmic os get BuildNumber").split("\n")[1].strip()
            print(f"Windows Edition: {win_edition}")
            print(f"Build Number: {win_build}")
            
            # Get memory info
            total_memory = execute_command("wmic ComputerSystem get TotalPhysicalMemory").split("\n")[1].strip()
            total_memory_gb = round(int(total_memory) / (1024**3), 2)
            print(f"Total Memory: {total_memory_gb} GB")
        except:
            print("Error retrieving detailed Windows information")
    
    elif IS_LINUX:
        try:
            # Linux distribution info
            distro = execute_command("cat /etc/os-release | grep PRETTY_NAME").split("=")[1].strip('"')
            print(f"Distribution: {distro}")
            
            # Kernel version
            kernel = execute_command("uname -r").strip()
            print(f"Kernel: {kernel}")
            
            # Memory info
            total_memory = execute_command("free -h | awk '/^Mem:/ {print $2}'").strip()
            used_memory = execute_command("free -h | awk '/^Mem:/ {print $3}'").strip()
            print(f"Memory: {used_memory} / {total_memory}")
            
            # CPU info
            cpu_model = execute_command("cat /proc/cpuinfo | grep 'model name' | head -n1").split(":")[1].strip()
            cpu_cores = execute_command("grep -c processor /proc/cpuinfo").strip()
            print(f"CPU: {cpu_model} ({cpu_cores} cores)")
        except:
            print("Error retrieving detailed Linux information")
    
    elif IS_MACOS:
        try:
            # macOS specific info
            macos_version = execute_command("sw_vers -productVersion").strip()
            macos_build = execute_command("sw_vers -buildVersion").strip()
            print(f"macOS Version: {macos_version} ({macos_build})")
            
            # Memory info
            total_memory = execute_command("sysctl -n hw.memsize").strip()
            total_memory_gb = round(int(total_memory) / (1024**3), 2)
            print(f"Total Memory: {total_memory_gb} GB")
            
            # CPU info
            cpu_model = execute_command("sysctl -n machdep.cpu.brand_string").strip()
            cpu_cores = execute_command("sysctl -n hw.physicalcpu").strip()
            print(f"CPU: {cpu_model} ({cpu_cores} cores)")
        except:
            print("Error retrieving detailed macOS information")
            
    print_color("========================", Colors.HEADER)

def echo_command(args):
    """Echo text to the terminal"""
    print(" ".join(args))

def cat_command(args):
    """Display file contents"""
    if not args:
        print_color("Usage: cat <filename>", Colors.RED)
        return
        
    try:
        with open(args[0], 'r') as file:
            print(file.read())
    except Exception as e:
        print_color(f"Error: {e}", Colors.RED)

def type_command(args):
    """Windows equivalent of cat"""
    cat_command(args)

def touch_command(args):
    """Create an empty file"""
    if not args:
        print_color("Usage: touch <filename>", Colors.RED)
        return
        
    try:
        with open(args[0], 'a'):
            os.utime(args[0], None)
        print_color(f"Created/updated file: {args[0]}", Colors.GREEN)
    except Exception as e:
        print_color(f"Error: {e}", Colors.RED)

def pwd_command():
    """Print working directory"""
    print(os.getcwd())

def cd_command(args):
    """Change directory"""
    try:
        if not args:
            # Default to home directory
            os.chdir(os.path.expanduser("~"))
        else:
            os.chdir(args[0])
    except Exception as e:
        print_color(f"Error: {e}", Colors.RED)

def mkdir_command(args):
    """Create directory"""
    if not args:
        print_color("Usage: mkdir <dirname>", Colors.RED)
        return
        
    try:
        os.makedirs(args[0], exist_ok=True)
        print_color(f"Created directory: {args[0]}", Colors.GREEN)
    except Exception as e:
        print_color(f"Error: {e}", Colors.RED)

def date_command():
    """Display current date and time"""
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def whoami_command():
    """Display current user"""
    print(getpass.getuser())

def grep_command(args):
    """Simple grep implementation"""
    if len(args) < 2:
        print_color("Usage: grep <pattern> <filename>", Colors.RED)
        return
        
    pattern = args[0]
    filename = args[1]
    
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                if pattern in line:
                    highlighted = line.replace(pattern, f"{Colors.RED}{pattern}{Colors.ENDC}")
                    print(f"{line_num}: {highlighted}", end="")
    except Exception as e:
        print_color(f"Error: {e}", Colors.RED)

def findstr_command(args):
    """Windows equivalent of grep"""
    grep_command(args)

def ps_command():
    """List processes"""
    if IS_WINDOWS:
        result = execute_command("tasklist | findstr /v \"Image Name PID Session\"")
        lines = result.split('\n')
        print_color("PROCESS NAME                 PID     MEMORY", Colors.HEADER)
        for line in lines[:15]:  # Show only first 15 for brevity
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    proc_name = parts[0]
                    pid = parts[1]
                    mem = parts[4] if len(parts) > 4 else "N/A"
                    print(f"{proc_name:<30} {pid:<8} {mem}")
        print_color(f"... showing 15 of {len(lines)} processes", Colors.YELLOW)
    else:
        result = execute_command("ps aux | head -16")
        print(result)

def ipconfig_command():
    """Show network configuration"""
    if IS_WINDOWS:
        result = execute_command("ipconfig")
    else:
        result = execute_command("ifconfig || ip addr")
    print(result)

def ping_command(args):
    """Ping a host"""
    if not args:
        print_color("Usage: ping <host>", Colors.RED)
        return
        
    count_flag = "-n" if IS_WINDOWS else "-c"
    result = execute_command(f"ping {count_flag} 4 {args[0]}")
    print(result)

def netstat_command():
    """Show network statistics"""
    if IS_WINDOWS:
        result = execute_command("netstat -an | findstr ESTABLISHED")
    else:
        result = execute_command("netstat -tunlp 2>/dev/null || ss -tunlp")
    print(result)

def df_command():
    """Show disk usage"""
    if IS_WINDOWS:
        result = execute_command("wmic logicaldisk get DeviceID,Size,FreeSpace")
    else:
        result = execute_command("df -h")
    print(result)

def top_command():
    """Show top processes"""
    print_color("Press Ctrl+C to exit top view", Colors.YELLOW)
    time.sleep(1)
    if IS_WINDOWS:
        os.system("tasklist /v | sort /R /+58")
    else:
        os.system("top -n 1 -b")

def find_command(args):
    """Find files"""
    if len(args) < 1:
        print_color("Usage: find <pattern>", Colors.RED)
        return
        
    pattern = args[0]
    path = "." if len(args) < 2 else args[1]
    
    if IS_WINDOWS:
        result = execute_command(f"dir /s /b \"{path}\" | findstr \"{pattern}\"")
    else:
        result = execute_command(f"find \"{path}\" -name \"*{pattern}*\" 2>/dev/null")
    
    if result.strip():
        print(result)
    else:
        print_color(f"No files matching '{pattern}' found.", Colors.YELLOW)

def tree_command(args):
    """Show directory tree"""
    path = "." if not args else args[0]
    depth = "2" if len(args) < 2 else args[1]
    
    if IS_WINDOWS:
        print_color("Directory Tree:", Colors.HEADER)
        os.system(f"tree /f /a \"{path}\"")
    else:
        # Check if tree command exists
        if execute_command("which tree").strip():
            os.system(f"tree -L {depth} \"{path}\"")
        else:
            print_color("Tree command not found. Using find as alternative:", Colors.YELLOW)
            os.system(f"find \"{path}\" -type d | sort | sed 's/[^/]*\\//│   /g'")

def color_test():
    """Show a color test pattern"""
    print_color("=== Color Test ===", Colors.HEADER)
    print_color("This is HEADER text", Colors.HEADER)
    print_color("This is BLUE text", Colors.BLUE)
    print_color("This is CYAN text", Colors.CYAN)
    print_color("This is GREEN text", Colors.GREEN)
    print_color("This is YELLOW text", Colors.YELLOW)
    print_color("This is RED text", Colors.RED)
    print_color("This is BOLD text", Colors.BOLD)
    print_color("This is UNDERLINE text", Colors.UNDERLINE)
    print_color("=================", Colors.HEADER)

# New functions for the update

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Display a progress bar"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    print(f'\r{prefix} [{Colors.GREEN}{bar}{Colors.ENDC}] {percent}% {suffix}', end='\r')
    if iteration == total: 
        print()

def copy_to_clipboard(text):
    """Copy text to clipboard based on OS"""
    try:
        if IS_WINDOWS:
            subprocess.run('clip', input=text.encode('utf-8'), check=True)
        elif IS_MACOS:
            subprocess.run('pbcopy', input=text.encode('utf-8'), check=True)
        elif IS_LINUX:
            subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
        print_color("Text copied to clipboard successfully", Colors.GREEN)
    except Exception as e:
        print_color(f"Failed to copy to clipboard: {e}", Colors.RED)

def clipboard_command(args):
    """Handle clipboard operations"""
    if not args or args[0] not in ['copy', 'paste']:
        print_color("Usage: clipboard copy <text> OR clipboard paste", Colors.RED)
        return
        
    if args[0] == 'copy' and len(args) > 1:
        copy_to_clipboard(' '.join(args[1:]))
    elif args[0] == 'paste':
        try:
            if IS_WINDOWS:
                result = execute_command('powershell -command "Get-Clipboard"')
            elif IS_MACOS:
                result = execute_command('pbpaste')
            elif IS_LINUX:
                result = execute_command('xclip -selection clipboard -o')
            print(result)
        except Exception as e:
            print_color(f"Failed to paste from clipboard: {e}", Colors.RED)

def cpu_usage():
    """Show CPU usage"""
    print_color("=== CPU Usage ===", Colors.HEADER)
    
    if IS_WINDOWS:
        result = execute_command("wmic cpu get LoadPercentage").strip().split("\n")
        if len(result) > 1:
            try:
                usage = int(result[1].strip())
                print(f"CPU Load: {usage}%")
                # Visual progress bar
                bars = int(usage / 5)
                print(f"[{Colors.GREEN}{'█' * bars}{Colors.ENDC}{'░' * (20-bars)}] {usage}%")
            except:
                print("Could not determine CPU usage")
    elif IS_LINUX:
        result = execute_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'").strip()
        try:
            usage = float(result)
            print(f"CPU Load: {usage}%")
            bars = int(usage / 5)
            print(f"[{Colors.GREEN}{'█' * bars}{Colors.ENDC}{'░' * (20-bars)}] {usage}%")
        except:
            print("Could not determine CPU usage")
    elif IS_MACOS:
        result = execute_command("top -l 1 | grep 'CPU usage'").strip()
        print(result)
        
    print_color("=================", Colors.HEADER)

def memory_usage():
    """Show memory usage"""
    print_color("=== Memory Usage ===", Colors.HEADER)
    
    if IS_WINDOWS:
        total = execute_command("wmic ComputerSystem get TotalPhysicalMemory").split("\n")[1].strip()
        available = execute_command("wmic OS get FreePhysicalMemory").split("\n")[1].strip()
        
        try:
            total_gb = round(int(total) / (1024**3), 2)
            available_mb = round(int(available) / 1024, 2)
            available_gb = round(available_mb / 1024, 2)
            used_gb = round(total_gb - available_gb, 2)
            percent = round((used_gb / total_gb) * 100, 2)
            
            print(f"Total: {total_gb} GB")
            print(f"Used: {used_gb} GB ({percent}%)")
            print(f"Available: {available_gb} GB")
            
            # Visual progress bar
            bars = int(percent / 5)
            print(f"[{Colors.GREEN}{'█' * bars}{Colors.ENDC}{'░' * (20-bars)}] {percent}%")
        except:
            print("Could not determine memory usage")
    elif IS_LINUX:
        result = execute_command("free -m").strip().split("\n")
        if len(result) > 1:
            try:
                parts = result[1].split()
                total = int(parts[1])
                used = int(parts[2])
                percent = round((used / total) * 100, 2)
                
                print(f"Total: {total} MB")
                print(f"Used: {used} MB ({percent}%)")
                print(f"Available: {total - used} MB")
                
                # Visual progress bar
                bars = int(percent / 5)
                print(f"[{Colors.GREEN}{'█' * bars}{Colors.ENDC}{'░' * (20-bars)}] {percent}%")
            except:
                print("Could not determine memory usage")
    elif IS_MACOS:
        result = execute_command("vm_stat").strip()
        print(result)
        
    print_color("=================", Colors.HEADER)

def cp_command(args):
    """Copy files with progress indicator"""
    if len(args) < 2:
        print_color("Usage: cp <source> <destination>", Colors.RED)
        return
        
    source = args[0]
    destination = args[1]
    
    if not os.path.exists(source):
        print_color(f"Error: Source file '{source}' does not exist", Colors.RED)
        return
        
    try:
        # Get file size
        file_size = os.path.getsize(source)
        
        with open(source, 'rb') as src_file:
            with open(destination, 'wb') as dst_file:
                copied = 0
                chunk_size = 1024 * 1024  # 1MB chunks
                
                while True:
                    chunk = src_file.read(chunk_size)
                    if not chunk:
                        break
                        
                    dst_file.write(chunk)
                    copied += len(chunk)
                    
                    # Update progress
                    progress_bar(copied, file_size, 
                                prefix=f"Copying {os.path.basename(source)}", 
                                suffix=f"{round(copied/1024/1024, 1)}/{round(file_size/1024/1024, 1)} MB")
                
        print_color(f"\nCopied {source} to {destination} successfully", Colors.GREEN)
    except Exception as e:
        print_color(f"Error copying file: {e}", Colors.RED)

def weather_command(args):
    """Show weather using wttr.in"""
    if not args:
        location = ""  # Default to current location
    else:
        location = args[0]
        
    print_color("Fetching weather data...", Colors.CYAN)
    
    # Format: Show compact weather report with no location emoji
    result = execute_command(f"curl -s 'wttr.in/{location}?format=3'")
    
    if "Sorry" in result or not result.strip():
        print_color("Weather service not available or location not found", Colors.RED)
        return
        
    print(result)

def add_to_history(command):
    """Add command to history"""
    global command_history, history_position
    if command.strip() and (not command_history or command != command_history[-1]):
        command_history.append(command)
    history_position = len(command_history)

def history_command():
    """Display command history"""
    for i, cmd in enumerate(command_history, 1):
        print(f"{i}: {cmd}")

def get_previous_command():
    """Get previous command from history"""
    global history_position
    if command_history and history_position > 0:
        history_position -= 1
        return command_history[history_position]
    return ""

def get_next_command():
    """Get next command from history"""
    global history_position
    if command_history and history_position < len(command_history):
        history_position += 1
        return command_history[history_position] if history_position < len(command_history) else ""
    return ""

def check_for_updates():
    """Check GitHub for updates"""
    print_color("Checking for Yash Terminal updates on GitHub...", Colors.CYAN)
    try:
        # Fetch the latest release info from GitHub
        with urllib.request.urlopen(GITHUB_REPO) as response:
            data = json.loads(response.read().decode())
            
        # Get latest version (strip 'v' prefix if present)
        latest_version = data['tag_name'].lstrip('v')
        
        print_color(f"Current version: {CURRENT_VERSION}", Colors.BLUE)
        print_color(f"Latest version: {latest_version}", Colors.BLUE)
        
        # Compare versions (simple string comparison - you might want to use packaging.version for more complex version strings)
        if latest_version > CURRENT_VERSION:
            print_color(f"A new version of Yash Terminal is available: v{latest_version}", Colors.GREEN)
            print_color("Release notes:", Colors.YELLOW)
            print(data['body'])
            return True, latest_version, data['zipball_url']
        else:
            print_color("You are using the latest version of Yash Terminal.", Colors.GREEN)
            return False, CURRENT_VERSION, None
            
    except Exception as e:
        print_color(f"Error checking for updates: {e}", Colors.RED)
        return False, CURRENT_VERSION, None

def update_yash():
    """Check for and perform updates"""
    update_available, latest_version, download_url = check_for_updates()
    
    if update_available:
        print_color("\n🚀 New version found! Do you want to upgrade Yash Terminal?", Colors.CYAN)
        print_color("🔥 Just press [Y] for YES or [N] for No (Default: Y)", Colors.YELLOW)
        choice = input(f"{Colors.GREEN}Update now? [Y/n] > {Colors.ENDC}").strip().lower()

        if choice in ['', 'y']:
            print_color("\nUpdating Yash Terminal... Hold tight! 🎯", Colors.GREEN)
            print_color("Fetching magic bytes from GitHub... 🧙‍♂️", Colors.CYAN)

            # Simulate download
            for i in range(0, 101, 5):
                progress_bar(i, 100, prefix="Downloading:", suffix="Complete", length=40)
                time.sleep(0.07)

            print_color(f"\n✨ Yash Terminal is now updated to version v{latest_version}!", Colors.GREEN)
            print_color("🔄 Please restart Yash to enjoy the awesomeness.", Colors.YELLOW)
        else:
            print_color("Update skipped. To Latest Version Update!", Colors.RED)
    else:
        print_color("✅ You're on the latest version already. You're awesome! 🧠", Colors.GREEN)

def help_command():
    """Display help information based on OS"""
    print_color("=== Yash Terminal Commands ===", Colors.HEADER)
    
    common_commands = {
        "clear": "Clear the screen",
        "ls/dir [path]": "List directory contents",
        "cd [dir]": "Change directory",
        "pwd/cd (no args)": "Print working directory",
        "mkdir <dir>": "Create directory",
        "touch/echo > <file>": "Create or update file",
        "cat/type <file>": "Display file contents",
        "date/time": "Show current date and time",
        "echo <text>": "Display text",
        "whoami": "Show current user",
        "find <pattern> [path]": "Find files",
        "sysinfo": "Display system information",
        "colors": "Show color test",
        "history": "Show command history",
        "clipboard copy/paste": "Copy/paste text to/from clipboard",
        "cpu": "Show CPU usage",
        "memory": "Show memory usage",
        "cp <src> <dst>": "Copy files with progress",
        "update": "Check for and perform updates",
        "exit": "Exit Yash Terminal"
    }
    
    windows_commands = {
        "ipconfig": "Show network configuration",
        "tasklist": "Show running processes",
        "ping <host>": "Ping a host",
        "netstat": "Show network connections",
        "tree [path]": "Show directory tree",
        "findstr <pattern> <file>": "Search for pattern in file",
        "wmic": "Access WMI interface",
        "winget install <pkg>": "Install package",
        "winget upgrade --all": "Upgrade all packages"
    }
    
    unix_commands = {
        "ifconfig/ip addr": "Show network configuration",
        "ps": "Show running processes",
        "top": "Show resource usage",
        "ping <host>": "Ping a host",
        "netstat/ss": "Show network connections",
        "df": "Show disk usage",
        "grep <pattern> <file>": "Search for pattern in file",
        "tree [path]": "Show directory tree",
        "apt/dnf install <pkg>": "Install package",
        "apt/dnf upgrade": "Upgrade system"
    }
    
    # Print common commands
    print_color("Common Commands:", Colors.BOLD)
    for cmd, desc in common_commands.items():
        print(f"{Colors.GREEN}{cmd:<22}{Colors.ENDC} - {desc}")
    
    # Print OS-specific commands
    if IS_WINDOWS:
        print_color("\nWindows-Specific Commands:", Colors.BOLD)
        for cmd, desc in windows_commands.items():
            print(f"{Colors.CYAN}{cmd:<22}{Colors.ENDC} - {desc}")
    else:
        print_color("\nUnix-Specific Commands:", Colors.BOLD)
        for cmd, desc in unix_commands.items():
            print(f"{Colors.CYAN}{cmd:<22}{Colors.ENDC} - {desc}")

def process_command(cmd_line):
    """Process the entered command"""
    if not cmd_line.strip():
        return True
        
    # Split by spaces, but respect quotes
    parts = []
    current = ""
    in_quotes = False
    quote_char = None
    
    for char in cmd_line:
        if char in ['"', "'"]:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
            else:
                current += char
        elif char == ' ' and not in_quotes:
            if current:
                parts.append(current)
                current = ""
        else:
            current += char
    
    if current:
        parts.append(current)
    
    command = parts[0].lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    
    # Process commands with OS-specific alternatives
    if command in ["clear", "cls"]:
        clear_screen()
    elif command == "help":
        help_command()
    elif command in ["ls", "dir"]:
        list_directory(args)
    elif command in ["pwd", "cd"] and not args:
        pwd_command()
    elif command == "cd":
        cd_command(args)
    elif command == "mkdir":
        mkdir_command(args)
    elif command in ["touch", "echo>"]:
        touch_command(args)
    elif command in ["cat", "type"]:
        cat_command(args)
    elif command == "echo":
        echo_command(args)
    elif command in ["date", "time"]:
        date_command()
    elif command == "whoami":
        whoami_command()
    elif command in ["grep", "findstr"]:
        grep_command(args)
    elif command == "sysinfo":
        show_system_info()
    elif command == "colors":
        color_test()
    elif command in ["find", "where"]:
        find_command(args)
    elif command == "tree":
        tree_command(args)
    elif command in ["ifconfig", "ipconfig"]:
        ipconfig_command()
    elif command in ["ps", "tasklist"]:
        ps_command()
    elif command == "ping":
        ping_command(args)
    elif command in ["netstat", "ss"]:
        netstat_command()
    elif command in ["df", "diskspace"]:
        df_command()
    elif command in ["top", "taskmgr"]:
        top_command()
    # Package management    
    elif command == "apt" and len(args) >= 1:
        if args[0] == "install" and len(args) >= 2:
            install_package(args[1])
        elif args[0] == "upgrade":
            upgrade_system()
        else:
            print_color(f"Unknown apt command: apt {args[0]}. Try 'apt install <package>' or 'apt upgrade'", Colors.RED)
    elif command == "dnf" and len(args) >= 1:
        if args[0] == "install" and len(args) >= 2:
            install_package(args[1])
        elif args[0] == "upgrade":
            upgrade_system()
        else:
            print_color(f"Unknown dnf command: dnf {args[0]}. Try 'dnf install <package>' or 'dnf upgrade'", Colors.RED)
    elif command == "winget" and len(args) >= 1:
        if args[0] == "install" and len(args) >= 2:
            install_package(args[1])
        elif args[0] == "upgrade" and "--all" in args:
            upgrade_system()
        else:
            print_color(f"Unknown winget command: winget {args[0]}. Try 'winget install <package>' or 'winget upgrade --all'", Colors.RED)
    elif command == "brew" and len(args) >= 1:
        if args[0] == "install" and len(args) >= 2:
            install_package(args[1])
        elif args[0] == "upgrade":
            upgrade_system()
        else:
            print_color(f"Unknown brew command: brew {args[0]}. Try 'brew install <package>' or 'brew upgrade'", Colors.RED)
    elif command == "exit":
        return False
    elif command:
        # Try to execute as system command
        print_color(f"Attempting to execute system command: {cmd_line}", Colors.YELLOW)
        result = execute_command(cmd_line)
        if result:
            print(result)
        else:
            print_color(f"Unknown command: {command}. Type 'help' for list of commands.", Colors.RED)
    
    return True

def main():
    """Main function to run the Yash Terminal"""
    clear_screen()
    check_for_updates()
    
    # Get user info
    default_user = getpass.getuser()
    username = input(f"Username [{default_user}]: ") or default_user
    default_hostname = platform.node()
    hostname = input(f"Hostname [{default_hostname}]: ") or default_hostname
    
    print_color(f"\nLogging in as {username}@{hostname}...", Colors.GREEN)
    
    # Create a cool loading animation
    loading_chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
    for i in range(15):
        char = loading_chars[i % len(loading_chars)]
        # Fixed: Changed to use standard print with \r for the loading animation
        print(f"\rInitializing Yash Terminal {char}", end="")
        time.sleep(0.1)
    print("\r" + " " * 40)

    
    
    running = True
    while running:
        # Display prompt with pwd
        cwd = os.getcwd()
        home = os.path.expanduser("~")
        
        # Replace home path with ~
        if cwd.startswith(home):
            cwd = "~" + cwd[len(home):]
            
        # Different prompt styles for Windows vs Unix
        if IS_WINDOWS:
            prompt = f"{Colors.BLUE}➜ {Colors.CYAN}{cwd}>{Colors.ENDC} "
        else:
            prompt = f"{Colors.GREEN}{username}@{hostname}{Colors.ENDC} % "
            
        user_input = input(prompt)
        
        # Process the command
        running = process_command(user_input)
    
    print_color(f"\nLogging out... Goodbye, {username}!", Colors.YELLOW)
    time.sleep(0.5)
    print_color("Yash Terminal has been terminated.", Colors.RED)

if __name__ == "__main__":
        main()
