import subprocess
import os
import json
import re
from utils import speak
import config
from contacts import get_contacts
from .utils import get_launcher_activity, send_notification, find_contact_by_phone

def open_app(app_name):
    app_lower = app_name.lower()
    package = config.APP_NAME_TO_PACKAGE.get(app_lower, app_name)
    print(f"Opening {app_name} ({package})")
    speak(f"Opening {app_name}")
    component = get_launcher_activity(package)
    cmd = ["am", "start", "--user", "0", "-n", component] if component else ["am", "start", "-p", package]
    try:
        subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        print(f"Error opening app: {e}")

def run_shell(command):
    print(f"Shell: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        if result.stdout: print(result.stdout)
        if result.stderr: print(result.stderr)
        speak("Command executed")
    except Exception as e:
        print(f"Error: {e}")

def get_call_log(limit=10):
    try:
        result = subprocess.run(["termux-call-log", "-l", str(limit)], capture_output=True, text=True, check=True)
        calls = json.loads(result.stdout)
        for i, call in enumerate(calls, 1):
            name = call.get('name', call.get('phone_number', 'Unknown'))
            print(f"{i}. {name} ({call.get('type')}) - {call.get('date')}")
        speak(f"Found {len(calls)} calls")
    except Exception as e:
        print(f"Error: {e}")

def get_sms_inbox(limit=10):
    try:
        result = subprocess.run(["termux-sms-list", "-l", str(limit)], capture_output=True, text=True, check=True)
        messages = json.loads(result.stdout)
        for i, msg in enumerate(messages, 1):
            sender = find_contact_by_phone(msg.get('address')) or msg.get('address')
            print(f"{i}. From {sender}: {msg.get('body')[:30]}...")
        speak(f"Found {len(messages)} messages")
    except Exception as e:
        print(f"Error: {e}")

def list_contacts(limit=20):
    from contacts import get_contacts
    contacts = get_contacts()
    show = contacts[:limit] if limit > 0 else contacts
    for i, c in enumerate(show, 1):
        print(f"{i}. {c.get('original_name')} - {c.get('phone')}")
    speak(f"Found {len(show)} contacts")

def show_toast(text):
    subprocess.run(["termux-toast", text])

def set_wallpaper(image_path):
    try:
        subprocess.run(["termux-wallpaper", image_path], check=True)
        speak("Wallpaper updated")
    except:
        pass
