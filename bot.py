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

    if "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback.get("message", {}).get("chat", {}).get("id")
        data = callback.get("data", "")
        user_id = callback.get("from", {}).get("id")

        if user_id != TELEGRAM_ADMIN_ID:
            send_telegram(chat_id, "⛔ Unauthorized")
            answer_callback(callback.get("id"))
            return "OK", 200

        if data.startswith("gen_"):
            _, count, days = data.split("_")
            new_keys = generate_new_keys(int(count), int(days), "standard")
            response = f"✅ <b>Generated {count} Key(s)</b>\n\n" + "\n".join([f"<code>{k}</code>" for k in new_keys])
            send_telegram(chat_id, response)
        elif data.startswith("global_"):
            _, days = data.split("_")
            day_count = int(days)
            new_keys = generate_new_keys(1, day_count, f"global_{day_count}")
            response = f"🌍 <b>Global Key ({day_count} Days)</b>\n\n<code>{new_keys[0]}</code>"
            send_telegram(chat_id, response)
        elif data == "toggle_server":
            toggle_setting(chat_id, "server_enabled", "Server")
        elif data == "toggle_validation":
            toggle_setting(chat_id, "key_validation_enabled", "Validation")
        elif data == "toggle_creation":
            toggle_setting(chat_id, "key_creation_enabled", "Creation")
        elif data == "menu_main":
            send_main_menu(chat_id)
        elif data == "menu_generate":
            send_generate_menu(chat_id)
        elif data == "menu_global":
            send_global_menu(chat_id)
        elif data == "menu_control":
            send_control_menu(chat_id)
        elif data == "menu_stats":
            send_status(chat_id)

        answer_callback(callback.get("id"))
        return "OK", 200
    
    if "message" in update:
        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "").strip()
        user_id = msg.get("from", {}).get("id")

        if user_id != TELEGRAM_ADMIN_ID:
            send_telegram(chat_id, "⛔ Unauthorized")
            return "OK", 200

        if text == "/start":
            send_main_menu(chat_id)
        elif text == "/menu":
            send_main_menu(chat_id)
        elif text == "/generate":
            send_generate_menu(chat_id)
        elif text == "/global":
            send_global_menu(chat_id)
        elif text == "/control":
            send_control_menu(chat_id)
        elif text == "/status":
            send_status(chat_id)
        elif text.startswith("/gen"):
            parts = text.split()
            count = int(parts[1]) if len(parts) > 1 else 1
            days = int(parts[2]) if len(parts) > 2 else 30
            new_keys = generate_new_keys(count, days, "standard")
            response = f"✅ <b>Generated {count} Key(s)</b>\n\n" + "\n".join([f"<code>{k}</code>" for k in new_keys])
            send_telegram(chat_id, response)

    return "OK", 200

# --- Helpers ---
def generate_new_keys(count, days, key_type):
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
            "type": key_type
        })
        created_keys.append(key_str)
    
    save_data(data)
    return created_keys

def send_telegram(chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    )

def send_telegram_with_keyboard(chat_id, text, keyboard):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": keyboard,
        },
    )

def answer_callback(callback_id):
    if not callback_id:
        return
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
        json={"callback_query_id": callback_id},
    )

def send_main_menu(chat_id):
    text = (
        "🤖 <b>ST FAMILY Control Panel</b>\n\n"
        "اختر خيارًا من القائمة:"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔑 Generate Keys", "callback_data": "menu_generate"},
                {"text": "🌍 Global Keys", "callback_data": "menu_global"},
            ],
            [
                {"text": "⚙️ Control Server", "callback_data": "menu_control"},
                {"text": "📊 Status", "callback_data": "menu_stats"},
            ],
        ]
    }
    send_telegram_with_keyboard(chat_id, text, keyboard)

def send_generate_menu(chat_id):
    text = "🔑 <b>Generate Standard Keys</b>"
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "1 Key • 7 Days", "callback_data": "gen_1_7"},
                {"text": "1 Key • 30 Days", "callback_data": "gen_1_30"},
            ],
            [
                {"text": "5 Keys • 30 Days", "callback_data": "gen_5_30"},
                {"text": "10 Keys • 30 Days", "callback_data": "gen_10_30"},
            ],
            [
                {"text": "⬅️ Back", "callback_data": "menu_main"},
            ],
        ]
    }
    send_telegram_with_keyboard(chat_id, text, keyboard)

def send_global_menu(chat_id):
    text = "🌍 <b>Global Keys (Unlimited Devices)</b>"
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Global • 1 Day", "callback_data": "global_1"},
                {"text": "Global • 7 Days", "callback_data": "global_7"},
            ],
            [
                {"text": "Global • 30 Days", "callback_data": "global_30"},
            ],
            [
                {"text": "⬅️ Back", "callback_data": "menu_main"},
            ],
        ]
    }
    send_telegram_with_keyboard(chat_id, text, keyboard)

def send_control_menu(chat_id):
    data = load_data()
    settings = data.get("settings", {})
    server = settings.get("server_enabled", True)
    validation = settings.get("key_validation_enabled", True)
    creation = settings.get("key_creation_enabled", True)

    text = "⚙️ <b>Server Controls</b>"
    keyboard = {
        "inline_keyboard": [
            [
                {"text": f"{'🟢' if server else '🔴'} Server", "callback_data": "toggle_server"},
                {"text": f"{'🟢' if validation else '🔴'} Validation", "callback_data": "toggle_validation"},
            ],
            [
                {"text": f"{'🟢' if creation else '🔴'} Creation", "callback_data": "toggle_creation"},
            ],
            [
                {"text": "⬅️ Back", "callback_data": "menu_main"},
            ],
        ]
    }
    send_telegram_with_keyboard(chat_id, text, keyboard)

def toggle_setting(chat_id, key, label):
    data = load_data()
    settings = data.get("settings", {})
    current = settings.get(key, True)
    settings[key] = not current
    data["settings"] = settings
    save_data(data)
    status = "Enabled" if settings[key] else "Disabled"
    send_telegram(chat_id, f"{label} ➜ <b>{status}</b>")
    send_control_menu(chat_id)

def send_status(chat_id):
    data = load_data()
    total = len(data.get("keys", []))
    settings = data.get("settings", {})
    text = (
        "📊 <b>Status</b>\n\n"
        f"Total Keys: {total}\n"
        f"Server: {'🟢' if settings.get('server_enabled', True) else '🔴'}\n"
        f"Validation: {'🟢' if settings.get('key_validation_enabled', True) else '🔴'}\n"
        f"Creation: {'🟢' if settings.get('key_creation_enabled', True) else '🔴'}"
    )
    send_telegram(chat_id, text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
