# --- All required libraries are built into Python ---
import urllib.request
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

# --- App & State Configuration ---
app = Flask(__name__)

app_state = {
    "notifications_on": True,
    "sound_on": True, # Separate state for sound
    "message": "🔔 Ding Dong! Someone is at the door!",
    "last_ring_time": "Never",
    "ring_event_id": 0 # Used to signal a new ring to the web page
}

# --- ⚙️ START HERE: Configuration ---
# Paste your Telegram Bot Token and Chat ID directly into the quotes below.
BOT_TOKEN = "7953955314:AAF5yw28fyVxPQ_Gr0JizKQAhYugJ-JC3c8"
CHAT_ID = "-4693626510"
# --- ⚙️ END HERE: Configuration ---

def send_telegram_notification(message):
    """Sends a message to your Telegram bot using only built-in Python libraries."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("🔴 ERROR: Please update BOT_TOKEN and CHAT_ID in the app.py file.")
        return False

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message}).encode('utf-8')

    try:
        req = urllib.request.Request(api_url, data=payload, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print("✅ Telegram notification sent successfully.")
                return True
            else:
                print(f"🔴 ERROR: Telegram API returned status {response.status}")
                return False
    except Exception as e:
        print(f"🔴 ERROR: Failed to send Telegram notification: {e}")
        return False

def trigger_ring_logic():
    """Contains the core logic for a doorbell ring event, callable from multiple routes."""
    # Increment event ID to signal a new ring to the web UI
    app_state['ring_event_id'] += 1
    app_state['last_ring_time'] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    # Independent check for Telegram notifications
    if app_state['notifications_on']:
        print("🔵 Notifications are ON. Sending Telegram message.")
        send_telegram_notification(app_state['message'])

    # This response is for the ESP32, but we can return it for consistency.
    if app_state['sound_on']:
        print("🔊 Physical buzzer is ON. Replying with BUZZ.")
        return "BUZZ"
    else:
        print("🔇 Physical buzzer is OFF. Replying with SILENT.")
        return "SILENT"

# --- Web Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles the main control panel page."""
    if request.method == 'POST':
        app_state['notifications_on'] = 'notifications_on' in request.form
        app_state['sound_on'] = 'sound_on' in request.form # Handle the new sound toggle
        app_state['message'] = request.form.get('message', app_state['message'])
        print(f"⚙️ Settings updated: Notifications {'ON' if app_state['notifications_on'] else 'OFF'}, Sound {'ON' if app_state['sound_on'] else 'OFF'}")
        return redirect(url_for('index'))

    return render_template('index.html',
                           notifications_on=app_state['notifications_on'],
                           sound_on=app_state['sound_on'], # Pass sound state to template
                           message=app_state['message'],
                           last_ring=app_state['last_ring_time'])

@app.route('/ring', methods=['GET'])
def ring_doorbell():
    """This is the endpoint the ESP32 calls."""
    print("\n🔔 Doorbell ring received from ESP32!")    
    return trigger_ring_logic()

@app.route('/test_ring', methods=['POST'])
def test_ring():
    """Allows triggering a ring from the web UI for testing."""
    print("\n🔔 Test ring triggered from web UI!")
    trigger_ring_logic()
    # The web UI doesn't need the "BUZZ"/"SILENT" response,
    # so we just return a success status.
    return jsonify({'status': 'ok'}), 200

@app.route('/status')
def status():
    """Provides the current status to the web UI for polling."""
    return jsonify({
        'last_ring_time': app_state['last_ring_time'],
        'ring_event_id': app_state['ring_event_id'],
        'sound_on': app_state['sound_on']
    })

# --- Main Execution ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5120, debug=True)