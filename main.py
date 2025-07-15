
# Main entry point to run the Telegram bot
import os
import sys
import time
import subprocess
import signal

# Check for running instances and kill them
def kill_existing_instances():
    try:
        # Find Python processes that might be running the bot
        output = subprocess.check_output("ps aux | grep python | grep telegram", shell=True).decode()
        lines = output.strip().split('\n')
        
        # Get current process ID
        current_pid = os.getpid()
        
        for line in lines:
            if 'grep' in line:  # Skip the grep process itself
                continue
                
            parts = line.split()
            if len(parts) > 1:
                pid = int(parts[1])
                
                # Don't kill current process
                if pid != current_pid:
                    print(f"Killing existing bot instance with PID {pid}")
                    try:
                        os.kill(pid, signal.SIGTERM)
                        # Wait to ensure process is terminated
                        time.sleep(1)
                        # If still running, force kill
                        try:
                            os.kill(pid, 0)  # Check if process exists
                            os.kill(pid, signal.SIGKILL)  # Force kill
                        except OSError:
                            pass  # Process already terminated
                    except Exception as e:
                        print(f"Error killing process {pid}: {e}")
    except Exception as e:
        # If any error occurs, just continue
        print(f"Error checking for existing processes: {e}")
        pass

# Add the current directory to the path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Kill any existing bot instances
    kill_existing_instances()
    
    # Set the Telegram token from environment
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if TELEGRAM_TOKEN:
        os.environ["TELEGRAM_TOKEN"] = TELEGRAM_TOKEN
    else:
        print("No TELEGRAM_BOT_TOKEN found in environment")
    
    # Note: Webhook deletion handled by the bot itself
    
    # Import after setting the token
    from enhanced_bot_v3 import main
    
    # Start the bot
    main()
