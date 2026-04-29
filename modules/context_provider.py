# modules/context_provider.py
import subprocess
import json
from datetime import datetime

def get_battery_context():
    """Get battery percentage and status."""
    try:
        res = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
        data = json.loads(res.stdout)
        return f"Battery: {data.get('percentage')}% ({data.get('status')})"
    except:
        return "Battery: Unknown"

def get_wifi_context():
    """Get current WiFi SSID."""
    try:
        res = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True)
        data = json.loads(res.stdout)
        return f"WiFi: {data.get('ssid', 'Disconnected')}"
    except:
        return "WiFi: Unknown"

def get_location_context():
    """Get coarse location (last known)."""
    # Note: real location can be slow, so we might want to skip or use a cached value
    return "Location: Termux Environment"

def get_smart_context(categories):
    """
    Assembles relevant device context based on the intent categories.
    """
    context_parts = []
    
    # Always include time
    now = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
    context_parts.append(f"Current time: {now}")
    
    # Lazy load based on categories
    if "information" in categories or "device" in categories:
        context_parts.append(get_battery_context())
        context_parts.append(get_wifi_context())
        
    # Add more logic for location etc.
    
    return "\n".join(context_parts)
