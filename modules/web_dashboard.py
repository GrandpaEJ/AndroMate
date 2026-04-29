import os
import sys

# Ensure sibling modules can be imported when run directly or via -m
if __package__ is None or __package__ == "":
    # Run directly
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
else:
    # Run as -m modules.web_dashboard
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    modules_dir = os.path.join(parent_dir, "modules")
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)

import traceback
import logging
import io
import subprocess
import json
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for

import config
from ai import ask_ai
from actions import execute_action
import memory

# Suppress Flask's default request logs (werkzeug) by setting its logger to WARNING
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

app = Flask(__name__, static_folder='static', template_folder='templates')

# Folder for generated images (relative to this file)
app.config['GENERATED_FOLDER'] = os.path.join(os.path.dirname(__file__), 'generated')
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Set up our own logger (optional, for errors)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.route('/')
def index():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return "Template not found. Check that templates/dashboard.html exists.", 500

@app.route('/generated/<filename>')
def serve_generated(filename):
    """Serve generated images."""
    return send_from_directory(app.config['GENERATED_FOLDER'], filename)

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    user_input = data.get('command', '').strip() if data else ''
    if not user_input:
        return jsonify({'output': '', 'error': 'Empty command'})

    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    error = None
    trace = None
    result = None
    thought = ""
    try:
        decision = ask_ai(user_input, context="web")
        thought = decision.get('thought', '')
        result = execute_action(decision, context="web")
        
        # If the action was a reply, the stdout might be empty, so we use decision['response']
        ai_response = decision.get('response', '')
    except Exception as e:
        error = str(e)
        trace = traceback.format_exc()
        logger.error(f"Command error: {error}")
    finally:
        sys.stdout = old_stdout

    captured_output = new_stdout.getvalue()
    # Prefer captured stdout (from execute_action), fallback to ai_response
    final_output = captured_output if captured_output.strip() else ai_response
    
    response_data = {
        'output': final_output, 
        'thought': thought,
        'error': error, 
        'trace': trace
    }

    # If the result is an image file, copy it to generated folder and return URL
    if result and isinstance(result, str) and os.path.exists(result):
        # Generate a unique filename to avoid collisions
        base = os.path.basename(result)
        dest = os.path.join(app.config['GENERATED_FOLDER'], base)
        # If file already exists, add a number suffix
        counter = 1
        while os.path.exists(dest):
            name, ext = os.path.splitext(base)
            dest = os.path.join(app.config['GENERATED_FOLDER'], f"{name}_{counter}{ext}")
            counter += 1
        shutil.copy2(result, dest)
        # Return URL relative to the server
        image_url = url_for('serve_generated', filename=os.path.basename(dest))
        response_data['image'] = image_url

    return jsonify(response_data)

@app.route('/api/status', methods=['GET'])
def status():
    status_data = {}
    try:
        battery = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
        if battery.returncode == 0:
            data = json.loads(battery.stdout)
            status_data['battery'] = data.get('percentage', 'unknown')
            status_data['battery_status'] = data.get('status', 'unknown')
    except:
        status_data['battery'] = 'unknown'

    try:
        wifi = subprocess.run(["termux-wifi-connectioninfo"], capture_output=True, text=True)
        if wifi.returncode == 0:
            data = json.loads(wifi.stdout)
            status_data['wifi'] = data.get('ssid', 'Not connected')
            status_data['wifi_ip'] = data.get('ip', '')
    except:
        status_data['wifi'] = 'unknown'

    try:
        storage = subprocess.run(["df", "-h", "/data/data/com.termux/files"], capture_output=True, text=True)
        if storage.returncode == 0:
            lines = storage.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 4:
                    status_data['storage_used'] = parts[1]
                    status_data['storage_total'] = parts[3]
    except:
        pass

    try:
        mem = subprocess.run(["free", "-m"], capture_output=True, text=True)
        if mem.returncode == 0:
            lines = mem.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 2:
                    status_data['memory_used'] = parts[1]
    except:
        pass

    try:
        network = subprocess.run(["termux-telephony-deviceinfo"], capture_output=True, text=True)
        if network.returncode == 0:
            data = json.loads(network.stdout)
            status_data['network_type'] = data.get('network_type', 'Unknown')
            status_data['operator'] = data.get('operator_name', 'Unknown')
    except:
        pass

    return jsonify(status_data)


QUICK_ACTIONS = [
    {"id": "call_logs", "name": "Call Logs", "icon": "fa-phone-rotary", "command": "show call logs"},
    {"id": "sms_inbox", "name": "SMS Inbox", "icon": "fa-message", "command": "show sms inbox"},
    {"id": "contacts", "name": "All Contacts", "icon": "fa-address-book", "command": "show all contacts"},
    {"id": "selfie", "name": "Take Selfie", "icon": "fa-camera", "command": "take a selfie"},
    {"id": "torch", "name": "Toggle Torch", "icon": "fa-lightbulb", "command": "toggle torch"},
    {"id": "brightness", "name": "Brightness", "icon": "fa-sun", "command": "set brightness maximum"},
    {"id": "volume_up", "name": "Volume Up", "icon": "fa-volume-high", "command": "volume up"},
    {"id": "wifi_on", "name": "WiFi On", "icon": "fa-wifi", "command": "turn on wifi"},
    {"id": "clipboard", "name": "Read Clipboard", "icon": "fa-clipboard", "command": "read clipboard"},
    {"id": "battery", "name": "Battery Status", "icon": "fa-battery-full", "command": "battery status"},
]


@app.route('/api/quick-actions', methods=['GET'])
def get_quick_actions():
    return jsonify(QUICK_ACTIONS)


@app.route('/api/quick-action', methods=['POST'])
def execute_quick_action():
    data = request.get_json()
    action_id = data.get('action_id')
    action = next((a for a in QUICK_ACTIONS if a['id'] == action_id), None)
    if not action:
        return jsonify({'error': 'Action not found'}), 400

    user_input = action['command']
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    error = None
    result = None
    thought = ""
    try:
        decision = ask_ai(user_input, context="web")
        thought = decision.get('thought', '')
        result = execute_action(decision, context="web")
        ai_response = decision.get('response', '')
    except Exception as e:
        error = str(e)
    finally:
        sys.stdout = old_stdout

    captured_output = new_stdout.getvalue()
    final_output = captured_output if captured_output.strip() else ai_response

    return jsonify({'output': final_output, 'error': error, 'thought': thought})


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        result = subprocess.run(["termux-contact-list"], capture_output=True, text=True)
        if result.returncode == 0:
            contacts = json.loads(result.stdout)
            return jsonify(contacts)
    except:
        pass
    return jsonify([])


@app.route('/api/provider', methods=['GET'])
def get_provider():
    try:
        config_path = os.path.expanduser("~/.andromate/config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = json.load(f)
                return jsonify({'provider': cfg.get('provider', 'pollinations')})
    except:
        pass
    return jsonify({'provider': 'pollinations'})


@app.route('/api/provider', methods=['POST'])
def set_provider():
    data = request.get_json()
    new_provider = data.get('provider', 'pollinations')
    try:
        config_path = os.path.expanduser("~/.andromate/config.json")
        cfg = {}
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = json.load(f)
        cfg['provider'] = new_provider
        with open(config_path, 'w') as f:
            json.dump(cfg, f)
        return jsonify({'success': True, 'provider': new_provider})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    try:
        memory.clear()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_web(host='127.0.0.1', port=5000, debug=False):
    """Start the Flask web server with a clean startup message."""
    print("\n" + "="*60)
    print("🚀 AndroMate Web Dashboard")
    print("="*60)
    print(f"🌐 Local URL: http://{host}:{port}")
    print("📱 Access from this device only (for security).")
    print("🔒 To access from other devices, use SSH tunnel or change host to 0.0.0.0 (not recommended).")
    print("="*60)
    print("Press Ctrl+C to stop the server.\n")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
