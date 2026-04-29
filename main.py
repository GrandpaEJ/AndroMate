# main.py
import sys
import os

# Add modules to path
modules_dir = os.path.join(os.path.dirname(__file__), 'modules')
sys.path.insert(0, modules_dir)

def show_menu():
    print("Welcome to AndroMate")
    print("1. CLI Mode")
    print("2. Web Dashboard")
    print("3. Telegram Bot")
    print("4. Voice Mode")
    print("5. Wake Word Detector")
    print("6. Background Monitor (Default)")
    print("q. Quit")
    
    choice = input("\nSelect an option: ").strip().lower()
    return choice

def main():
    choice = None
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = show_menu()

    if choice in ['1', 'cli']:
        from cli import run_cli
        run_cli()
    elif choice in ['2', 'web']:
        from web_dashboard import run_web
        run_web(host='127.0.0.1', port=5000, debug=False)
    elif choice in ['3', 'telegram', 'tg']:
        from telegram_bot import run_bot
        run_bot()
    elif choice in ['4', 'voice']:
        from voice import handle_voice_command
        handle_voice_command()
    elif choice in ['5', 'wake']:
        from wake_word import run_wake_detector
        run_wake_detector()
    elif choice in ['6', 'background', '']:
        # This imports from modules/main.py
        from main import main as bg_start
        bg_start()
    elif choice == 'q':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
