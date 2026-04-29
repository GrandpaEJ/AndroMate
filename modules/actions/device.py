import subprocess
import json
from utils import speak

def get_battery():
    try:
        result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        level = data.get('percentage', 'unknown')
        status = data.get('status', 'unknown')
        print(f"Battery status: {level}%, {status}")
        speak(f"Battery level is {level} percent, {status}")
    except Exception as e:
        print(f"Error getting battery status: {e}")
        speak("Sorry, I couldn't get the battery status.")

def set_brightness(level):
    try:
        subprocess.run(["termux-brightness", str(level)], check=True)
        print(f"Brightness set to {level}")
        speak(f"Brightness set to {level}")
    except Exception as e:
        print(f"Error setting brightness: {e}")

def toggle_torch(state, camera=None):
    if state.lower() not in ("on", "off"):
        return
    try:
        subprocess.run(["termux-torch", state.lower()], check=True)
        print(f"Torch turned {state}")
        speak(f"Torch turned {state}")
    except Exception as e:
        print(f"Error toggling torch: {e}")

def set_volume(stream, level):
    try:
        subprocess.run(["termux-volume", stream, str(level)], check=True)
        print(f"Volume for {stream} set to {level}")
        speak(f"{stream} volume set to {level}")
    except Exception as e:
        print(f"Error setting volume: {e}")

def get_wifi_info():
    try:
        result = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        ssid = data.get('ssid', 'unknown')
        ip = data.get('ip', 'unknown')
        print(f"WiFi: {ssid}, IP: {ip}")
        speak(f"Connected to {ssid}")
    except Exception as e:
        print(f"Error getting WiFi info: {e}")

def scan_wifi():
    try:
        result = subprocess.run(["termux-wifi-scaninfo"], capture_output=True, text=True, check=True)
        print("WiFi scan results:")
        print(result.stdout)
        speak("WiFi scan completed")
    except Exception as e:
        print(f"Error scanning WiFi: {e}")

def wifi_enable(state="true"):
    cmd_state = "true" if state.lower() in ("on", "true", "enable") else "false"
    try:
        subprocess.run(["termux-wifi-enable", cmd_state], check=True)
        print(f"WiFi turned {'on' if cmd_state == 'true' else 'off'}")
        speak(f"WiFi turned {'on' if cmd_state == 'true' else 'off'}")
    except Exception as e:
        print(f"Error toggling WiFi: {e}")

def get_location(provider="gps"):
    try:
        result = subprocess.run(["termux-location", "-p", provider], capture_output=True, text=True, check=True)
        print(result.stdout)
        data = json.loads(result.stdout)
        lat = data.get('latitude', 'unknown')
        lon = data.get('longitude', 'unknown')
        speak(f"Location: {lat}, {lon}")
    except Exception as e:
        print(f"Error getting location: {e}")
