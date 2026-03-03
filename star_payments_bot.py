import json
import os
import logging
import time
import psycopg2
from psycopg2.extras import Json
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Enable basic logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
TOKEN = "8771694472:AAElikaXxrelU67Fy-ZuchG9biFErvnZsas"  # <-- Replace with your Telegram Bot Token
ADMIN_ID = 123456789           # <-- Replace with YOUR Telegram User ID to see the Admin Panel

DATA_FILE = "stars_db.json"

# Conversation states for admin
AWAIT_FLUORIT_KEYS = 1
AWAIT_DRIP_KEYS = 2
AWAIT_HG_KEYS = 3

# ==========================================
# 💾 DATABASE FUNCTIONS
# ==========================================
DB_URL = "postgres://koyeb-adm:npg_JQV5YFgpM1ro@ep-wandering-forest-alq0up3o.c-3.eu-central-1.pg.koyeb.app/koyebdb"

def get_db_connection():
    return psycopg2.connect(DB_URL)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bot_state (
            id INTEGER PRIMARY KEY,
            data JSONB
        )
    ''')
    cur.execute('SELECT id FROM bot_state WHERE id = 1')
    if not cur.fetchone():
        default_data = {"fluorit_keys": [], "drip_keys": [], "hg_keys": [], "sales": [], "last_purchases": {}}
        cur.execute("INSERT INTO bot_state (id, data) VALUES (1, %s)", (Json(default_data),))
    conn.commit()
    cur.close()
    conn.close()

def load_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM bot_state WHERE id = 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"DB Load Error: {e}")
    return {"fluorit_keys": [], "drip_keys": [], "hg_keys": [], "sales": [], "last_purchases": {}}

def save_data(data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE bot_state SET data = %s WHERE id = 1", (Json(data),))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Save Error: {e}")

# Initialize DB on startup
init_db()

# ==========================================
# 🚀 CORE BOT HANDLERS
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command that everyone can use. No approval needed. Displays shop."""
    user = update.effective_user
    
    # Everyone gets these buttons
    keyboard = [
        [InlineKeyboardButton("🛍️ Buy Fluorit Key (1 Day) - 250 ⭐", callback_data="buy_fluorit")],
        [InlineKeyboardButton("🛍️ Buy Drip Key (1 Day) - 100 ⭐", callback_data="buy_drip")],
        [InlineKeyboardButton("🛍️ Buy HG Key (1 Day) - 100 ⭐", callback_data="buy_hg")],
        [InlineKeyboardButton("📢 Official Admin Channel", url="https://t.me/fakhreddinepoiwtoo")]
    ]
    
    # 🔐 Admin panel ONLY shows if the user ID matches ADMIN_ID
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("🔐 Admin Panel", callback_data="admin_menu")])
        keyboard.append([InlineKeyboardButton("📊 View Sales Activity", callback_data="admin_activity")])
        
    text = (
        f"Hello {user.first_name}!\n\n"
        "Welcome to the Key Shop. Here you can instantly buy **1-Day keys** using **Telegram Stars**.\n"
        "💳 Instant generation with Stars upon checkout!\n\n"
        "Please choose a product below:"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Routes the buttons clicked underneath the menu"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    db = load_data()

    # ---- COOLDOWN CHECK CHECK (48 HOURS) ----
    if data in ["buy_fluorit", "buy_drip", "buy_hg"]:
        last_purchase = db.get("last_purchases", {}).get(str(user_id), 0)
        elapsed = time.time() - last_purchase
        cooldown = 48 * 3600 # 48 hours
        if elapsed < cooldown:
            hours_left = int((cooldown - elapsed) // 3600)
            mins_left = int(((cooldown - elapsed) % 3600) // 60)
            await query.edit_message_text(
                f"⏳ **Cooldown Active!**\n\nYou must wait 48 hours between purchases.\n"
                f"Please wait: **{hours_left}h {mins_left}m** before buying again.\n\n"
                f"Contact the Admin on the Channel for help.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Contact Admin", url="https://t.me/fakhreddinepoiwtoo")],
                    [InlineKeyboardButton("⬅️ Back", callback_data="start")]
                ]),
                parse_mode="Markdown"
            )
            return ConversationHandler.END

    if data == "buy_fluorit":
        if not db.get("fluorit_keys"):
            await query.edit_message_text("❌ Sorry, Fluorit day keys are currently out of stock!",
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="start")]]))
            return ConversationHandler.END
        # 250 Stars price (Star currency amount is 1:1)
        await send_star_invoice(query.message.chat_id, context, "Fluorit", 250)
        
    elif data == "buy_drip":
        if not db.get("drip_keys"):
            await query.edit_message_text("❌ Sorry, Drip day keys are currently out of stock!",
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="start")]]))
            return ConversationHandler.END
        # 100 Stars price
        await send_star_invoice(query.message.chat_id, context, "Drip", 100)

    elif data == "buy_hg":
        if not db.get("hg_keys"):
            await query.edit_message_text("❌ Sorry, HG day keys are currently out of stock!",
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="start")]]))
            return ConversationHandler.END
        # 100 Stars price
        await send_star_invoice(query.message.chat_id, context, "HG", 100)

    elif data == "start":
        await start(update, context)

    # ------------------ ADMIN SECTION ------------------
    # --- Only Admin can view Sales
    elif data == "admin_activity" and user_id == ADMIN_ID:
        sales = db.get("sales", [])
        total_keys_sold = len(sales)
        total_stars = sum(s.get("stars_paid", 0) for s in sales)
        
        # Breakdown by product
        f_sold = sum(1 for s in sales if s.get("product") == "Fluorit")
        d_sold = sum(1 for s in sales if s.get("product") == "Drip")
        h_sold = sum(1 for s in sales if s.get("product") == "HG")
        
        text = (
            f"📊 **Global Sales Activity**\n\n"
            f"💰 **Total Earnings:** {total_stars} ⭐\n"
            f"🔑 **Total Keys Sold:** {total_keys_sold}\n\n"
            f"**Breakdown:**\n"
            f"- Fluorit: {f_sold} sold\n"
            f"- Drip: {d_sold} sold\n"
            f"- HG: {h_sold} sold\n"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="start")]]))


    elif data == "admin_menu" and user_id == ADMIN_ID:
        f_count = len(db.get("fluorit_keys", []))
        d_count = len(db.get("drip_keys", []))
        h_count = len(db.get("hg_keys", []))
        
        keyboard = [
            [InlineKeyboardButton(f"➕ Add Fluorit (In Stock: {f_count})", callback_data="admin_add_fluorit")],
            [InlineKeyboardButton(f"➕ Add Drip (In Stock: {d_count})", callback_data="admin_add_drip")],
            [InlineKeyboardButton(f"➕ Add HG (In Stock: {h_count})", callback_data="admin_add_hg")],
            [InlineKeyboardButton("⬅️ Back to Shop", callback_data="start")]
        ]
        await query.edit_message_text("🔐 **Admin Control Panel**\nAdd new Day Keys here:", 
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "admin_add_fluorit" and user_id == ADMIN_ID:
        await query.edit_message_text("Send me the **Fluorit Day Keys** now (one per line):", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="admin_menu")]]),
                                      parse_mode="Markdown")
        return AWAIT_FLUORIT_KEYS
        
    elif data == "admin_add_drip" and user_id == ADMIN_ID:
        await query.edit_message_text("Send me the **Drip Day Keys** now (one per line):", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="admin_menu")]]),
                                      parse_mode="Markdown")
        return AWAIT_DRIP_KEYS

    elif data == "admin_add_hg" and user_id == ADMIN_ID:
        await query.edit_message_text("Send me the **HG Day Keys** now (one per line):", 
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="admin_menu")]]),
                                      parse_mode="Markdown")
        return AWAIT_HG_KEYS

    return ConversationHandler.END

# ==========================================
# 💰 TELEGRAM STARS CHECKOUT LOGIC
# ==========================================
async def send_star_invoice(chat_id, context, product_name, star_price):
    """Sends a Telegram Stars invoice to the user."""
    title = f"{product_name} 1-Day Key"
    description = f"Instantly receive your {product_name} Day key after Star payment."
    payload = f"payment_{product_name.lower()}"
    
    # Telegram Stars Currency Code is 'XTR'
    currency = "XTR" 
    
    # Amount is simple integer representing stars
    prices = [LabeledPrice(title, star_price)]

    # provider_token must be EMPTY for Telegram Stars payments
    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="", 
        currency=currency,
        prices=prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fired when user clicks pay. Validates stock is still available."""
    query = update.pre_checkout_query
    payload = query.invoice_payload
    db = load_data()
    
    # Final validation just before withdrawing stars
    if payload == "payment_fluorit" and not db.get("fluorit_keys"):
        await query.answer(ok=False, error_message="Sorry! Fluorit keys literally just sold out.")
    elif payload == "payment_drip" and not db.get("drip_keys"):
        await query.answer(ok=False, error_message="Sorry! Drip keys literally just sold out.")
    elif payload == "payment_hg" and not db.get("hg_keys"):
        await query.answer(ok=False, error_message="Sorry! HG keys literally just sold out.")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Runs after stars are successfully deducted. Bot sends the key here."""
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    db = load_data()
    
    key = "ERROR_NO_KEY"
    product_type = ""
    
    # Pop key from DB
    if payload == "payment_fluorit" and db["fluorit_keys"]:
        key = db["fluorit_keys"].pop(0)
        product_type = "Fluorit"
    elif payload == "payment_drip" and db["drip_keys"]:
        key = db["drip_keys"].pop(0)
        product_type = "Drip"
    elif payload == "payment_hg" and db["hg_keys"]:
        key = db["hg_keys"].pop(0)
        product_type = "HG"
            
    # Save the transaction history
    db.setdefault("sales", []).append({
        "user_id": update.message.from_user.id,
        "username": update.message.from_user.username,
        "product": product_type,
        "key_given": key,
        "stars_paid": payment.total_amount
    })
    
    # Save timestamp for the 48-hour cooldown!
    db.setdefault("last_purchases", {})[str(update.message.from_user.id)] = time.time()
    save_data(db)
    
    # Deliver the key
    text = (
        f"🎉 **Payment Successful!** Thank you.\n\n"
        f"Here is your {product_type} 1-Day Key:\n"
        f"`{key}`\n\n"
        f"⚠️ *You will now have a 48 hour cooldown before you can buy another key.*\n\n"
        f"If you need help or have questions, contact the Admin Channel."
    )
    
    keyboard = [[InlineKeyboardButton("📢 Admin Channel", url="https://t.me/fakhreddinepoiwtoo")]]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ==========================================
# 📥 ADMIN KEY INGESTION
# ==========================================
async def handle_new_keys(update: Update, context: ContextTypes.DEFAULT_TYPE, product_type):
    """Takes plaintext message from Admin and adds it to stock"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return ConversationHandler.END
        
    new_keys = update.message.text.strip().split('\n')
    new_keys = [k.strip() for k in new_keys if k.strip()] # Remove empties
    
    db = load_data()
    if product_type == "fluorit":
        db.setdefault("fluorit_keys", []).extend(new_keys)
    elif product_type == "drip":
        db.setdefault("drip_keys", []).extend(new_keys)
    else:
        db.setdefault("hg_keys", []).extend(new_keys)
    save_data(db)
    
    await update.message.reply_text(f"✅ Successfully added {len(new_keys)} {product_type.capitalize()} keys!\nClick /start to view the menu.")
    return ConversationHandler.END

async def add_fluorit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_new_keys(update, context, "fluorit")

async def add_drip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_new_keys(update, context, "drip")

async def add_hg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_new_keys(update, context, "hg")

# ==========================================
# ⚙️ MAIN LOOP
# ==========================================
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Admin conversation handler for adding keys
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            AWAIT_FLUORIT_KEYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_fluorit)],
            AWAIT_DRIP_KEYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_drip)],
            AWAIT_HG_KEYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_hg)]
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    
    # Telegram Star Payment Handlers
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    print("Star Payments bot is running...")
    
    # ------------------ FAKE WEB SERVER FOR KOYEB ------------------
    # Koyeb requires port 8000 to respond to keep the bot alive!
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    class DummyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b"Bot is online and healthy!")
    def run_dummy_server():
        server_address = ('', int(os.environ.get('PORT', 8000)))
        httpd = HTTPServer(server_address, DummyHandler)
        httpd.serve_forever()
    threading.Thread(target=run_dummy_server, daemon=True).start()
    # -------------------------------------------------------------

    app.run_polling()

if __name__ == "__main__":
    main()
