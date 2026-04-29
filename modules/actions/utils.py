import re
import os
import subprocess
import json
from datetime import datetime
from contacts import get_contacts

def extract_phone_number(text):
    digits = re.sub(r'\D', '', text)
    if len(digits) >= 10:
        return digits
    return None

def normalize_phone(phone):
    return re.sub(r'\D', '', phone) if phone else ''

def find_contact_by_phone(phone_number):
    normalized = normalize_phone(phone_number)
    if not normalized:
        return None
    contacts = get_contacts()
    for c in contacts:
        c_phone = c.get('phone', '')
        if normalize_phone(c_phone) == normalized:
            return c.get('original_name')
    return None

def get_timestamp_filename(prefix="photo", ext="jpg"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"

def get_launcher_activity(package):
    try:
        result = subprocess.run(
            ["pm", "resolve-activity", "--brief", package],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split('\n')
        if lines and lines[0]:
            return lines[0].strip()
    except subprocess.CalledProcessError:
        pass
    return None

def send_notification(title, content):
    try:
        subprocess.run(["termux-notification", "--id", "andromate_action", "--title", title, "--content", content])
    except:
        pass
