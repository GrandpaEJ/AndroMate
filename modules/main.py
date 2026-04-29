import os
import sys

# Ensure sibling modules can be imported when run directly or via -m
if __package__ is None or __package__ == "":
    # Run directly
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
else:
    # Run as -m modules.main
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    modules_dir = os.path.join(parent_dir, "modules")
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

import time
import subprocess
from config import ENABLE_VOICE, ENABLE_NOTIFICATIONS, ENABLE_CLIPBOARD, POLL_INTERVAL
import voice
import notifications
import clipboard

def main():
    # Acquire wake lock
    subprocess.run(["termux-wake-lock"])
    print("AI Assistant started. Press Ctrl+C to stop.")

    previous_notif_ids = []
    last_clipboard = ""

    try:
        while True:
            if ENABLE_NOTIFICATIONS:
                previous_notif_ids = notifications.monitor_notifications(previous_notif_ids)
            if ENABLE_CLIPBOARD:
                last_clipboard = clipboard.monitor_clipboard(last_clipboard)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        subprocess.run(["termux-wake-unlock"])

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "voice":
        voice.handle_voice_command()
    else:
        main()
