import subprocess
import os
import re
from utils import speak
from .utils import get_timestamp_filename

def take_photo(filename=None, camera="back"):
    if not filename:
        filename = get_timestamp_filename("photo", "jpg")
    camera_arg = "1" if camera in ["front", "selfie"] else "0"
    try:
        subprocess.run(["termux-camera-photo", "-c", camera_arg, filename], check=True)
        abs_path = os.path.abspath(filename)
        print(f"Photo saved: {abs_path}")
        speak("Photo taken")
        return abs_path
    except Exception as e:
        print(f"Error taking photo: {e}")
        speak("Failed to take photo")
        return None

def media_control(cmd):
    try:
        subprocess.run(["termux-media-player", cmd], check=True)
        print(f"Media {cmd}")
        speak(f"Media {cmd}")
    except Exception as e:
        print(f"Error controlling media: {e}")

def generate_image(prompt):
    print(f"🎨 Generating image: '{prompt}'")
    speak("Generating image...")
    cmd = ["tgpt", "--provider", "arta", "--img", prompt]
    try:
        result = subprocess.run(cmd, input="y\n", capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        url_match = re.search(r'Image URL: (https?://[^\s]+)', output)
        if url_match:
            image_url = url_match.group(1)
            filename = image_url.split('/')[-1]
            local_path = os.path.join(os.getcwd(), filename)
            if os.path.exists(local_path):
                print(f"✅ Image saved: {local_path}")
                speak("Image generated")
                return local_path
        speak("Image generation failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    return None
