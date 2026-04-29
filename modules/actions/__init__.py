import os
import sys
from utils import speak
from . import communication, device, media, system

def execute_action(decision, context="general"):
    """
    Dispatcher for all actions.
    """
    action = decision.get('action', 'none')
    
    if action == 'send_sms':
        communication.send_sms(decision.get('recipient'), decision.get('message'))
    elif action == 'call':
        communication.call(decision.get('recipient'))
    elif action == 'send_whatsapp':
        communication.send_whatsapp(decision.get('recipient'), decision.get('message'))
    elif action == 'send_telegram':
        communication.send_telegram(decision.get('recipient'), decision.get('message'))
    elif action == 'send_email_smtp':
        communication.send_email_smtp(decision.get('recipient'), decision.get('subject'), decision.get('message'))
        
    elif action == 'open_app':
        system.open_app(decision.get('app'))
    elif action == 'run_shell':
        system.run_shell(decision.get('command'))
    elif action == 'show_toast':
        system.show_toast(decision.get('text'))
    elif action == 'set_wallpaper':
        system.set_wallpaper(decision.get('image_path'))
        
    elif action == 'get_battery':
        device.get_battery()
    elif action == 'set_brightness':
        device.set_brightness(decision.get('level'))
    elif action == 'toggle_torch':
        device.toggle_torch(decision.get('state'))
    elif action == 'set_volume':
        device.set_volume(decision.get('stream', 'music'), decision.get('level'))
    elif action == 'get_wifi_info':
        device.get_wifi_info()
    elif action == 'scan_wifi':
        device.scan_wifi()
    elif action == 'wifi_enable':
        device.wifi_enable(decision.get('state', 'on'))
    elif action == 'get_location':
        device.get_location(decision.get('provider', 'gps'))
        
    elif action == 'take_photo':
        return media.take_photo(camera=decision.get('camera', 'back'))
    elif action.startswith('media_'):
        cmd = action.replace('media_', '')
        media.media_control(cmd)
    elif action == 'generate_image':
        return media.generate_image(decision.get('prompt'))
        
    elif action == 'get_call_log':
        system.get_call_log(decision.get('limit', 10))
    elif action == 'get_sms_inbox':
        system.get_sms_inbox(decision.get('limit', 10))
    elif action == 'list_contacts':
        system.list_contacts(decision.get('limit', 20))
        
    elif action == 'reply':
        print(f"AndroMate: {decision.get('response')}")
        speak(decision.get('response'))
        
    return None

# Re-export key functions for direct use if needed
from .communication import send_sms, call, send_whatsapp, send_telegram, send_email_smtp
from .device import get_battery, set_brightness, toggle_torch, set_volume, get_wifi_info, scan_wifi, get_location
from .media import take_photo, generate_image
from .system import open_app, run_shell, show_toast, list_contacts, get_call_log, get_sms_inbox
