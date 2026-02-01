import os
import json
import random
import time
from datetime import datetime, timedelta, timezone
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Configuration ---
DATABASE_FILE = "key.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8216359066:AAEt2GFGgTBp3hh_znnJagH3h1nN5A_XQf0")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "7210704553"))

# --- Database Helper Functions ---
def load_db():
    if not os.path.exists(DATABASE_FILE):
        return {"settings": {"server_enabled": "1", "key_validation_enabled": "1", "key_creation_enabled": "1"}, "licenses": []}
    with open(DATABASE_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"settings": {"server_enabled": "1", "key_validation_enabled": "1", "key_creation_enabled": "1"}, "licenses": []}

def save_db(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_setting(key):
    db = load_db()
    return db["settings"].get(key, "1") == "1"

# --- Routes ---

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "Simple JSON License Server"})

@app.route('/validate', methods=['POST'])
def validate_key():
    payload = request.get_json(silent=True) or {}
    key_input = payload.get("key", "").strip()
    hwid_input = payload.get("hwid", "").strip()

    if not key_input or not hwid_input:
        return jsonify({"valid": False, "message": "Missing key or HWID"})

    if not get_setting("server_enabled"):
        return jsonify({"valid": False, "message": "Server Disabled"}), 503
    
    if not get_setting("key_validation_enabled"):
        return jsonify({"valid": False, "message": "Validation Disabled"})

    db = load_db()
    
    license_data = None
    for lic in db["licenses"]:
        if lic["license_key"] == key_input:
            license_data = lic
            break
            
    if not license_data:
        return jsonify({"valid": False, "message": "Invalid Key"})

    # Check Expiry
    if datetime.fromisoformat(license_data["expiry_date"]) < datetime.now(timezone.utc):
        return jsonify({"valid": False, "message": "Key Expired"})

    # Check Status
    if license_data.get("status") != "active":
        return jsonify({"valid": False, "message": "Key Banned/Inactive"})

    # Check HWID
    is_global = license_data["key_type"].startswith("global_")
    current_hwid = license_data.get("hwid")

    if not is_global:
        if current_hwid and current_hwid != hwid_input:
            return jsonify({"valid": False, "message": "HWID Mismatch"})
        
        # Link HWID if empty
        if not current_hwid:
            license_data["hwid"] = hwid_input
            save_db(db)

    return jsonify({
        "valid": True, 
        "message": "Key Active", 
        "expiry_date": license_data["expiry_date"]
    })

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    update = request.get_json(silent=True) or {}
    if not update: return "ok", 200

    message = update.get("message")
    callback = update.get("callback_query")

    if callback:
        handle_callback(callback)
    elif message:
        handle_message(message)

    return "ok", 200

# --- Logic ---

def handle_message(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "").strip()

    if user_id != TELEGRAM_ADMIN_ID:
        send_message(chat_id, "⛔ Authorization Failed")
        return

    if text == "/start":
        send_main_menu(chat_id)
    elif text == "/generate":
        send_gen_menu(chat_id)
    elif text == "/list":
        list_keys(chat_id)

def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    data = callback.get("data", "")
    
    if data.startswith("gen_"):
        _, count, days = data.split("_")
        generate_keys(chat_id, int(count), int(days))
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": callback["id"]})

def generate_keys(chat_id, count, days):
    db = load_db()
    new_keys = []
    expiry = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    
    for _ in range(count):
        k = f"{random.randint(0,0xFFFF):04X}-{random.randint(0,0xFFFF):04X}-{random.randint(0,0xFFFF):04X}-{random.randint(0,0xFFFF):04X}"
        db["licenses"].append({
            "license_key": k,
            "expiry_date": expiry,
            "key_type": "standard",
            "hwid": None,
            "status": "active"
        })
        new_keys.append(k)
    
    save_db(db)
    send_message(chat_id, f"✅ Generated {count} Keys:\n\n" + "\n".join([f"<code>{k}</code>" for k in new_keys]))

def list_keys(chat_id):
    db = load_db()
    msg = "🔑 <b>Active Keys:</b>\n\n"
    active_count = 0
    for lic in db["licenses"][-20:]: # Last 20
        msg += f"<code>{lic['license_key']}</code> ({lic.get('hwid', 'Unbound')})\n"
        active_count += 1
    
    if active_count == 0: msg = "No keys found."
    send_message(chat_id, msg)

# --- Telegram API ---
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=payload)

def send_main_menu(chat_id):
    send_message(chat_id, "🤖 <b>JSON Bot Manager</b>\n\n/generate - Create Keys\n/list - View Keys")

def send_gen_menu(chat_id):
    kb = {"inline_keyboard": [[{"text": "1 Key - 30 Days", "callback_data": "gen_1_30"}]]}
    send_message(chat_id, "Select Option:", reply_markup=kb)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
