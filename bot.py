import os
import json
import random
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Configuration ---
DATA_FILE = "key.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8216359066:AAEt2GFGgTBp3hh_znnJagH3h1nN5A_XQf0")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "7210704553"))

# --- Data Management ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"keys": [], "settings": {"server_enabled": True, "key_validation_enabled": True, "key_creation_enabled": True}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"keys": [], "settings": {"server_enabled": True, "key_validation_enabled": True, "key_creation_enabled": True}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Routes ---

@app.get("/")
def home():
    return "ST FAMILY License Server (Simple Mode) is Running!"

@app.post("/validate")
def validate_key():
    data = load_data()
    if not data["settings"].get("key_validation_enabled", True):
        return jsonify({"valid": False, "message": "Server maintenance"})

    payload = request.get_json(silent=True) or {}
    key_text = payload.get("key", "").strip()
    hwid = payload.get("hwid", "").strip()

    if not key_text or not hwid:
        return jsonify({"valid": False, "message": "Missing input"})

    # Find key
    found_key = None
    for k in data["keys"]:
        if k["key"] == key_text:
            found_key = k
            break
    
    if not found_key:
        return jsonify({"valid": False, "message": "Invalid key"})

    # Check expiry
    expiry = datetime.fromisoformat(found_key["expiry_date"])
    if datetime.now(timezone.utc) > expiry:
        return jsonify({"valid": False, "message": "Key expired"})

    # Check HWID
    if found_key.get("hwid") and found_key["hwid"] != hwid:
        # Allow global keys to bypass HWID check if type starts with global_
        if not found_key.get("type", "").startswith("global_"):
            return jsonify({"valid": False, "message": "Wrong device"})
    
    # Bind HWID if new
    if not found_key.get("hwid") and not found_key.get("type", "").startswith("global_"):
        found_key["hwid"] = hwid
        save_data(data)

    return jsonify({
        "valid": True,
        "message": "Key activated!",
        "expiry_date": found_key["expiry_date"]
    })

@app.post("/telegram-webhook")
def telegram_webhook():
    update = request.get_json(silent=True) or {}
    print(f"Update: {update}") 
    if not update: 
        return "OK", 200
    
    if "message" in update:
        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "").strip()
        user_id = msg.get("from", {}).get("id")

        if user_id != TELEGRAM_ADMIN_ID:
            send_telegram(chat_id, "? Unauthorized")
            return "OK", 200

        if text == "/start":
            send_telegram(chat_id, "?? <b>Owner Menu</b>\n\n/gen 1 30 - Generate 1 key for 30 days\n/status - Server Status")
        elif text.startswith("/gen"):
            # Format: /gen <count> <days>
            parts = text.split()
            count = 1
            days = 30
            if len(parts) > 1: count = int(parts[1])
            if len(parts) > 2: days = int(parts[2])
            
            new_keys = generate_new_keys(count, days)
            response = f"? <b>Generated {count} Key(s)</b>\n\n"
            for k in new_keys:
                response += f"<code>{k}</code>\n"
            send_telegram(chat_id, response)
        elif text == "/status":
            d = load_data()
            count = len(d["keys"])
            send_telegram(chat_id, f"?? <b>Status</b>\n\nTotal Keys: {count}")

    return "OK", 200

# --- Helpers ---
def generate_new_keys(count, days):
    data = load_data()
    expiry = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    created_keys = []
    
    for _ in range(count):
        key_str = "{:04X}-{:04X}-{:04X}-{:04X}".format(
            random.randint(0, 0xFFFF), random.randint(0, 0xFFFF),
            random.randint(0, 0xFFFF), random.randint(0, 0xFFFF)
        )
        data["keys"].append({
            "key": key_str,
            "expiry_date": expiry,
            "hwid": None,
            "type": "standard"
        })
        created_keys.append(key_str)
    
    save_data(data)
    return created_keys

def send_telegram(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
