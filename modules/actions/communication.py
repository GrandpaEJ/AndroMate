import subprocess
import re
import urllib.parse
import smtplib
from email.message import EmailMessage
import pathlib
import config
from contacts import match_contact
from utils import speak
from .utils import extract_phone_number, send_notification

def send_sms(recipient_name, message):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = contact['phone']
        subprocess.run(["termux-sms-send", "-n", number, message])
        print(f"SMS sent to {contact['original_name']} ({number}) : {message}")
        speak(f"SMS sent to {contact['original_name']}")
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            subprocess.run(["termux-sms-send", "-n", phone, message])
            print(f"SMS sent to {phone} (as direct number) : {message}")
            speak(f"SMS sent to {phone}")
        else:
            msg = f"No phone number for '{recipient_name}'. SMS not sent."
            print(msg)
            speak(msg)

def call(recipient_name):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = contact['phone']
        subprocess.run(["termux-telephony-call", number])
        print(f"Calling {contact['original_name']} ({number})")
        speak(f"Calling {contact['original_name']}")
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            subprocess.run(["termux-telephony-call", phone])
            print(f"Calling {phone} (as direct number)")
            speak(f"Calling {phone}")
        else:
            msg = f"No phone number for '{recipient_name}'. Call not placed."
            print(msg)
            speak(msg)

def send_whatsapp(recipient_name, message):
    contact, score = match_contact(recipient_name)
    if contact and contact['phone']:
        number = re.sub(r'[\s\-+]', '', contact['phone'])
        display_name = contact['original_name']
    else:
        phone = extract_phone_number(recipient_name)
        if phone:
            number = re.sub(r'[\s\-+]', '', phone)
            display_name = phone
        else:
            msg = f"No phone number for '{recipient_name}'. WhatsApp not sent."
            print(msg)
            speak(msg)
            return

    home_dir = pathlib.Path.home()
    wacli_db = home_dir / ".wacli" / "wacli.db"
    if wacli_db.exists():
        try:
            result = subprocess.run(
                ["wacli", "send", "text", "--to", number, "--message", message],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"WhatsApp sent to {display_name}: {message}")
                speak("WhatsApp message sent")
            else:
                err = f"Error sending WhatsApp: {result.stderr}"
                print(err)
                speak("Sorry, failed to send WhatsApp message.")
                send_notification("WhatsApp Error", err)
        except Exception as e:
            err = f"Error sending WhatsApp: {e}"
            print(err)
            speak("Sorry, couldn't send WhatsApp message.")
            send_notification("WhatsApp Error", err)
    else:
        # Fallback to xdg-open
        url = f"https://wa.me/{number}?text={urllib.parse.quote(message)}"
        subprocess.run(["xdg-open", url], check=True)
        print(f"WhatsApp opened for {display_name}.")
        speak(f"WhatsApp opened for {display_name}")

def send_telegram(recipient_name, message):
    contact, score = match_contact(recipient_name)
    number = contact['phone'] if contact and contact['phone'] else extract_phone_number(recipient_name)
    if number:
        number = re.sub(r'[\s\-+]', '', number)
        uri = f"tg://msg?text={urllib.parse.quote(message)}&to={number}"
        try:
            subprocess.run(["termux-open", uri], check=True)
            print(f"Telegram opened.")
            speak(f"Telegram opened")
        except Exception as e:
            print(f"Error opening Telegram: {e}")
    else:
        print(f"No phone number for '{recipient_name}'.")

def send_email_smtp(recipient, subject, body):
    sender = config.EMAIL_SENDER
    password = config.EMAIL_APP_PASSWORD
    if not sender or not password:
        print("Email credentials not configured.")
        speak("Email not configured.")
        return
    try:
        email = EmailMessage()
        email["From"] = sender
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(email)
        print(f"Email sent to {recipient}")
        speak("Email sent.")
    except Exception as e:
        print(f"Error sending email: {e}")
        speak("Failed to send email.")
