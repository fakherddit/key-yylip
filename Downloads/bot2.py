import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InputFile
import telegram
import os
from datetime import datetime
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Read from environment variables
TOKEN = os.getenv("TOKEN_BOT_2", "8216359066:AAG5awNOda7BbYaT_fclc-tZBvNTWuqht98")
ADMIN_CODE = os.getenv("ADMIN_CODE", "123123NNK")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pharm_db_qwum_user:ORxhLJpvjSumWLWQGDaqjQKEWUDeVFls@dpg-d5jp8vili9vc73bk3vcg-a.oregon-postgres.render.com/pharm_db_qwum")

SIGNATURE = "\n\n© @FAKHERDDIN5"
SELLER_CHANNEL_URL = "https://t.me/stonexff"

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        # Seller Design table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS seller_designs (
                design_id SERIAL PRIMARY KEY,
                seller_id BIGINT UNIQUE,
                color TEXT DEFAULT '#0000FF',
                welcome_message TEXT,
                button_style TEXT DEFAULT 'normal',
                logo_url TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        conn.commit()
        print("Seller designs table initialized!")
    except Exception as e:
        print(f"Error initializing seller designs: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def load_data():
    conn = get_db_connection()
    if not conn:
        return {
            "balances": {},
            "sellers": {},
            "keys": {},
            "users": [],
            "files": {},
            "sales_log": [],
            "start_clicks": 0,
            "used_keys": []
        }
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    data = {
        "balances": {},
        "sellers": {},
        "keys": {},
        "users": [],
        "files": {},
        "sales_log": [],
        "start_clicks": 0,
        "used_keys": []
    }
    
    try:
        # Load users and balances
        cur.execute('SELECT user_id, balance FROM users')
        for row in cur.fetchall():
            data["balances"][str(row['user_id'])] = row['balance']
            data["users"].append(str(row['user_id']))
        
        # Load sellers
        cur.execute('SELECT seller_id, name, balance, sales_count FROM sellers')
        for row in cur.fetchall():
            data["sellers"][str(row['seller_id'])] = {
                "name": row['name'],
                "balance": row['balance'],
                "sales_count": row['sales_count']
            }
        
        # Load keys
        cur.execute('SELECT product, duration, key_value, is_used FROM keys ORDER BY created_at')
        for row in cur.fetchall():
            key_name = f"{row['product']}_{row['duration']}"
            if key_name not in data["keys"]:
                data["keys"][key_name] = []
            data["keys"][key_name].append(row['key_value'])
            if row['is_used']:
                data["used_keys"].append(row['key_value'])
        
        # Load sales log
        cur.execute('SELECT buyer_id, product, duration, qty, unit_price, total_price, seller_id, buyer_balance FROM sales_log ORDER BY created_at DESC LIMIT 100')
        for row in cur.fetchall():
            data["sales_log"].append({
                "user": str(row['buyer_id']),
                "product": row['product'],
                "duration": str(row['duration']),
                "qty": row['qty'],
                "unit_price": row['unit_price'],
                "total_price": row['total_price'],
                "seller_id": str(row['seller_id']) if row['seller_id'] else None,
                "buyer_balance": row['buyer_balance']
            })
        
        # Load stats
        cur.execute('SELECT start_clicks FROM stats LIMIT 1')
        row = cur.fetchone()
        if row:
            data["start_clicks"] = row['start_clicks']
    
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        cur.close()
        conn.close()
    
    return data

def save_data(data):
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    try:
        # Update or insert users and balances
        for uid, balance in data.get("balances", {}).items():
            cur.execute('''
                INSERT INTO users (user_id, balance)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET balance = %s
            ''', (int(uid), balance, balance))
        
        # Update sellers
        for sid, info in data.get("sellers", {}).items():
            cur.execute('''
                INSERT INTO sellers (seller_id, name, balance, sales_count)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (seller_id) DO UPDATE SET 
                    name = %s, balance = %s, sales_count = %s
            ''', (int(sid), info.get("name"), info.get("balance", 0), info.get("sales_count", 0),
                  info.get("name"), info.get("balance", 0), info.get("sales_count", 0)))
        
        # Update start_clicks
        cur.execute('UPDATE stats SET start_clicks = %s WHERE stat_id = 1', 
                   (data.get("start_clicks", 0),))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving data: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def load_prices():
    conn = get_db_connection()
    if not conn:
        return {
            "global": {
                "FREE": {"1": 3, "7": 7, "31": 13},
                "WIZARD": {"1": 3, "7": 7, "31": 13},
                "DRIP": {"1": 2, "7": 5, "15": 8, "31": 12},
                "CERT": {"365": 6},
            },
            "sellers": {}
        }
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    prices = {"global": {}, "sellers": {}}
    
    try:
        # Load global prices
        cur.execute('SELECT product, duration, price FROM prices WHERE seller_id IS NULL')
        for row in cur.fetchall():
            if row['product'] not in prices["global"]:
                prices["global"][row['product']] = {}
            prices["global"][row['product']][str(row['duration'])] = row['price']
        
        # If no global prices, load defaults
        if not prices["global"]:
            default = {
                "FREE": {"1": 3, "7": 7, "31": 13},
                "WIZARD": {"1": 3, "7": 7, "31": 13},
                "DRIP": {"1": 2, "7": 5, "15": 8, "31": 12},
                "CERT": {"365": 6},
            }
            prices["global"] = default
            save_prices(prices)
        
        # Load seller prices
        cur.execute('SELECT seller_id, product, duration, price FROM prices WHERE seller_id IS NOT NULL')
        for row in cur.fetchall():
            sid = str(row['seller_id'])
            if sid not in prices["sellers"]:
                prices["sellers"][sid] = {}
            if row['product'] not in prices["sellers"][sid]:
                prices["sellers"][sid][row['product']] = {}
            prices["sellers"][sid][row['product']][str(row['duration'])] = row['price']
    
    except Exception as e:
        print(f"Error loading prices: {e}")
    finally:
        cur.close()
        conn.close()
    
    return prices

def save_prices(prices):
    conn = get_db_connection()
    if not conn:
        print("❌ No database connection available")
        return
    
    cur = conn.cursor()
    try:
        # Clear existing prices
        cur.execute('DELETE FROM prices')
        
        # Save global prices
        for product, durations in prices.get("global", {}).items():
            for duration, price in durations.items():
                cur.execute('''
                    INSERT INTO prices (product, duration, price)
                    VALUES (%s, %s, %s)
                ''', (product, int(duration), float(price)))
        
        # Save seller prices
        for seller_id, products in prices.get("sellers", {}).items():
            for product, durations in products.items():
                for duration, price in durations.items():
                    cur.execute('''
                        INSERT INTO prices (product, duration, seller_id, price)
                        VALUES (%s, %s, %s, %s)
                    ''', (product, int(duration), int(seller_id), float(price)))
        
        conn.commit()
        print(f"✅ Prices saved: {len(prices.get('sellers', {}))} sellers")
    except Exception as e:
        print(f"❌ Error saving prices: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_seller_design(seller_id):
    """الحصول على تصميم البائع"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    design = None
    try:
        cur.execute('SELECT color, welcome_message, button_style, logo_url FROM seller_designs WHERE seller_id = %s', (int(seller_id),))
        design = cur.fetchone()
    except Exception as e:
        print(f"Error loading seller design: {e}")
    finally:
        cur.close()
        conn.close()
    
    return design

def save_seller_design(seller_id, color, welcome_message, button_style, logo_url):
    """حفظ تصميم البائع"""
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO seller_designs (seller_id, color, welcome_message, button_style, logo_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (seller_id) DO UPDATE SET 
                color = %s, welcome_message = %s, button_style = %s, logo_url = %s
        ''', (int(seller_id), color, welcome_message, button_style, logo_url,
              color, welcome_message, button_style, logo_url))
        conn.commit()
    except Exception as e:
        print(f"Error saving seller design: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def key_storage_name(prod, dur):
    return f"{prod}_{dur}"

def add_keys_to_db(product, duration, keys):
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    try:
        for key in keys:
            cur.execute('''
                INSERT INTO keys (product, duration, key_value)
                VALUES (%s, %s, %s)
                ON CONFLICT (key_value) DO NOTHING
            ''', (product, int(duration), key))
        conn.commit()
    except Exception as e:
        print(f"Error adding keys: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_available_keys(product, duration, count):
    conn = get_db_connection()
    if not conn:
        return []
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    keys = []
    try:
        cur.execute('''
            SELECT key_id, key_value FROM keys 
            WHERE product = %s AND duration = %s AND is_used = FALSE 
            LIMIT %s
        ''', (product, int(duration), count))
        keys = [row['key_value'] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error getting keys: {e}")
    finally:
        cur.close()
        conn.close()
    
    return keys

def mark_keys_used(keys, buyer_id):
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    try:
        for key in keys:
            cur.execute('''
                UPDATE keys SET is_used = TRUE, sold_to = %s, sold_at = NOW()
                WHERE key_value = %s
            ''', (int(buyer_id), key))
        conn.commit()
    except Exception as e:
        print(f"Error marking keys as used: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def log_sale(buyer_id, product, duration, qty, unit_price, total_price, seller_id, buyer_balance):
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO sales_log (buyer_id, product, duration, qty, unit_price, total_price, seller_id, buyer_balance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (int(buyer_id), product, int(duration), qty, unit_price, total_price, 
              int(seller_id) if seller_id else None, buyer_balance))
        conn.commit()
    except Exception as e:
        print(f"Error logging sale: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_price(prices, product, duration, seller_id=None):
    duration = str(duration)
    if seller_id:
        seller_prices = prices.get("sellers", {}).get(seller_id, {})
        if product in seller_prices and duration in seller_prices[product]:
            return seller_prices[product][duration]
    return prices.get("global", {}).get(product, {}).get(duration)

def get_uid_from_update(update: Update):
    try:
        if getattr(update, "message", None) and update.message.from_user:
            return str(update.message.from_user.id)
        if getattr(update, "callback_query", None) and update.callback_query.from_user:
            return str(update.callback_query.from_user.id)
    except Exception:
        return None

# ========== HANDLERS ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ar")
    uid = get_uid_from_update(update)
    
    if uid:
        DATA = load_data()
        if uid not in DATA.get("users", []):
            DATA.setdefault("users", []).append(uid)
            DATA["balances"][uid] = 0
            save_data(DATA)
        
        DATA["start_clicks"] = DATA.get("start_clicks", 0) + 1
        save_data(DATA)
    
    button_texts = {
        "buy": {"en": "🛍️ BUY KEYS", "ar": "🛍️ شراء مفاتيح"},
        "balance": {"en": "💰 MY BALANCE", "ar": "💰 رصيدي"},
        "admin": {"en": "🔐 ADMIN PANEL", "ar": "🔐 لوحة الادمن"},
        "lang": {"en": "🌐 Change Language", "ar": "🌐 تغيير اللغة"},
    }
    
    reply_keyboard = [
        [button_texts["buy"][lang]],
        [button_texts["balance"][lang]],
        [button_texts["admin"][lang]],
        [button_texts["lang"][lang]]
    ]
    
    welcome_msg = "مرحباً بك في بوت المبيعات!" if lang == "ar" else "Welcome to Sales Bot!"
    
    if getattr(update, "message", None):
        await update.message.reply_text(welcome_msg + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
    else:
        await update.callback_query.message.reply_text(welcome_msg + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass
    
    data = getattr(query, "data", None)
    DATA = load_data()
    PRICES = load_prices()
    
    # Admin menu
    if data == "admin_menu":
        admin_keyboard = [
            [InlineKeyboardButton("💳 Add Balance", callback_data="admin_add_balance")],
            [InlineKeyboardButton("🔑 Add Keys", callback_data="admin_add_keys")],
            [InlineKeyboardButton("⚙️ Change Seller Price", callback_data="admin_change_seller_prices")],
            [InlineKeyboardButton("📊 Quick Price ±$1", callback_data="admin_quick_price")],
            [InlineKeyboardButton("🎨 Seller Design", callback_data="admin_seller_design")],
            [InlineKeyboardButton("📊 Statistics", callback_data="show_activity")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]
        ]
        await query.edit_message_text("قائمة الأدمن:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(admin_keyboard))
        return
    
    # Add Balance
    if data == "admin_add_balance":
        context.user_data["admin_action"] = "add_balance"
        await query.edit_message_text("أدخل معرف المستخدم والمبلغ (مثال: 123456789 10):" + SIGNATURE)
        return
    
    # Add Keys
    if data == "admin_add_keys":
        PRICES = load_prices()
        products = list(PRICES.get("global", {}).keys())
        keyboard = []
        for prod in products:
            keyboard.append([InlineKeyboardButton(prod, callback_data=f"admin_add_keys_product:{prod}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
        await query.edit_message_text("اختر المنتج:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    if data and data.startswith("admin_add_keys_product:"):
        product = data.split(":")[1]
        PRICES = load_prices()
        durations = list(PRICES.get("global", {}).get(product, {}).keys())
        keyboard = []
        for dur in durations:
            keyboard.append([InlineKeyboardButton(f"{dur} يوم", callback_data=f"admin_add_keys_duration:{product}:{dur}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")])
        await query.edit_message_text(f"اختر المدة للمنتج {product}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Buy product - select duration
    if data and data.startswith("buy_product:"):
        product = data.split(":")[1]
        PRICES = load_prices()
        durations = list(PRICES.get("global", {}).get(product, {}).keys())
        keyboard = []
        for dur in durations:
            price = get_price(PRICES, product, dur)
            keyboard.append([InlineKeyboardButton(f"{dur} يوم - ${price}", callback_data=f"buy_duration:{product}:{dur}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")])
        await query.edit_message_text(f"🛍️ اختر مدة الاشتراك - {product}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Buy duration - select quantity
    if data and data.startswith("buy_duration:"):
        parts = data.split(":")
        product = parts[1]
        duration = parts[2]
        PRICES = load_prices()
        price = get_price(PRICES, product, duration)
        
        keyboard = []
        for qty in [1, 3, 5, 10]:
            total = qty * price
            keyboard.append([InlineKeyboardButton(f"{qty}x - ${total}", callback_data=f"buy_qty:{product}:{duration}:{qty}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"buy_product:{product}")])
        await query.edit_message_text(f"📦 اختر الكمية:\n\nالمنتج: {product}\nالمدة: {duration} يوم\nالسعر الواحد: ${price}" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Buy finalize
    if data and data.startswith("buy_qty:"):
        parts = data.split(":")
        product = parts[1]
        duration = parts[2]
        qty = int(parts[3])
        uid = str(query.from_user.id)
        PRICES = load_prices()
        price = get_price(PRICES, product, duration)
        total_price = qty * price
        
        DATA = load_data()
        balance = DATA.get("balances", {}).get(uid, 0)
        
        if balance < total_price:
            await query.edit_message_text(f"❌ رصيدك غير كافي!\n\nرصيدك: ${balance}\nالمطلوب: ${total_price}" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
            return
        
        # Get keys
        keys = get_available_keys(product, duration, qty)
        if len(keys) < qty:
            await query.edit_message_text(f"❌ لا توجد مفاتيح كافية!\n\nالمتوفر: {len(keys)}\nالمطلوب: {qty}" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
            return
        
        # Deduct balance and mark keys
        DATA["balances"][uid] = balance - total_price
        save_data(DATA)
        mark_keys_used(keys, uid)
        log_sale(uid, product, duration, qty, price, total_price, None, DATA["balances"][uid])
        
        keys_text = "\n".join(keys)
        msg = f"✅ تم الشراء بنجاح!\n\n"
        msg += f"المنتج: {product}\n"
        msg += f"المدة: {duration} يوم\n"
        msg += f"الكمية: {qty}\n"
        msg += f"السعر الواحد: ${price}\n"
        msg += f"الإجمالي: ${total_price}\n"
        msg += f"رصيدك الجديد: ${DATA['balances'][uid]}\n\n"
        msg += f"🔑 المفاتيح:\n{keys_text}"
        
        await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
        return
    
    if data and data.startswith("admin_add_keys_duration:"):
        parts = data.split(":")
        product = parts[1]
        duration = parts[2]
        context.user_data["admin_action"] = "add_keys"
        context.user_data["add_keys_product"] = product
        context.user_data["add_keys_duration"] = duration
        await query.edit_message_text(f"أرسل المفاتيح (كل مفتاح في سطر) للمنتج {product} المدة {duration}:" + SIGNATURE)
        return
    
    # Change seller prices - Step 1: Select Seller
    if data == "admin_change_seller_prices":
        sellers = DATA.get("sellers", {})
        if not sellers:
            await query.edit_message_text("لا يوجد بائعون" + SIGNATURE)
            return
        
        keyboard = []
        for sid, info in sellers.items():
            keyboard.append([InlineKeyboardButton(f"{info.get('name')} ({sid})", callback_data=f"price_seller:{sid}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
        await query.edit_message_text("اختر البائع:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Quick Price Adjust - Select Seller
    if data == "admin_quick_price":
        sellers = DATA.get("sellers", {})
        if not sellers:
            await query.edit_message_text("لا يوجد بائعون" + SIGNATURE)
            return
        
        keyboard = []
        for sid, info in sellers.items():
            keyboard.append([InlineKeyboardButton(f"💰 {info.get('name')}", callback_data=f"quick_price_seller:{sid}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
        await query.edit_message_text("اختر البائع لتعديل السعر:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Quick Price - Select Product
    if data and data.startswith("quick_price_seller:"):
        seller_id = data.split(":")[1]
        products = list(PRICES.get("global", {}).keys())
        
        keyboard = []
        for prod in products:
            keyboard.append([InlineKeyboardButton(prod, callback_data=f"quick_price_product:{seller_id}:{prod}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_quick_price")])
        await query.edit_message_text(f"اختر المنتج:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Quick Price - Select Duration
    if data and data.startswith("quick_price_product:"):
        parts = data.split(":")
        seller_id = parts[1]
        product = parts[2]
        
        durations = list(PRICES.get("global", {}).get(product, {}).keys())
        keyboard = []
        for dur in durations:
            current_price = get_price(PRICES, product, dur, seller_id)
            default_price = PRICES.get("global", {}).get(product, {}).get(dur, 0)
            price_text = current_price if current_price else default_price
            keyboard.append([InlineKeyboardButton(f"{dur} يوم - ${price_text}", callback_data=f"quick_price_adjust:{seller_id}:{product}:{dur}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"quick_price_seller:{seller_id}")])
        await query.edit_message_text(f"اختر المدة:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Quick Price - Adjust (+/-)
    if data and data.startswith("quick_price_adjust:"):
        parts = data.split(":")
        seller_id = parts[1]
        product = parts[2]
        duration = parts[3]
        
        current_price = get_price(PRICES, product, duration, seller_id)
        default_price = PRICES.get("global", {}).get(product, {}).get(duration, 0)
        price_text = current_price if current_price else default_price
        
        keyboard = [
            [InlineKeyboardButton("➕ +$1", callback_data=f"quick_price_inc:{seller_id}:{product}:{duration}")],
            [InlineKeyboardButton("➖ -$1", callback_data=f"quick_price_dec:{seller_id}:{product}:{duration}")],
            [InlineKeyboardButton("⬅️ Back", callback_data=f"quick_price_product:{seller_id}:{product}")]
        ]
        
        msg = f"تعديل السعر:\n\n"
        msg += f"البائع: {seller_id}\n"
        msg += f"المنتج: {product}\n"
        msg += f"المدة: {duration} يوم\n"
        msg += f"السعر الحالي: ${price_text}"
        
        await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Quick Price - Increase
    if data and data.startswith("quick_price_inc:"):
        parts = data.split(":")
        seller_id = parts[1]
        product = parts[2]
        duration = parts[3]
        
        # Reload prices to get current value
        PRICES = load_prices()
        current_price = get_price(PRICES, product, duration, seller_id)
        default_price = PRICES.get("global", {}).get(product, {}).get(duration, 0)
        old_price = float(current_price if current_price else default_price)
        new_price = old_price + 1
        
        # Update database
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute('''
                    DELETE FROM prices 
                    WHERE seller_id = %s AND product = %s AND duration = %s
                ''', (int(seller_id), product, int(duration)))
                
                cur.execute('''
                    INSERT INTO prices (product, duration, seller_id, price)
                    VALUES (%s, %s, %s, %s)
                ''', (product, int(duration), int(seller_id), float(new_price)))
                
                conn.commit()
                print(f"✅ Price increased: Seller {seller_id}, {product} {duration}d: {old_price} → {new_price}")
            except Exception as db_err:
                print(f"❌ DB Error: {db_err}")
                conn.rollback()
            finally:
                cur.close()
                conn.close()
        
        msg = f"✅ تم زيادة السعر!\n\n"
        msg += f"البائع: {seller_id}\n"
        msg += f"المنتج: {product}\n"
        msg += f"المدة: {duration} يوم\n"
        msg += f"${old_price} → ${new_price}"
        
        await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_quick_price")]]))
        return
    
    # Quick Price - Decrease
    if data and data.startswith("quick_price_dec:"):
        parts = data.split(":")
        seller_id = parts[1]
        product = parts[2]
        duration = parts[3]
        
        # Reload prices to get current value
        PRICES = load_prices()
        current_price = get_price(PRICES, product, duration, seller_id)
        default_price = PRICES.get("global", {}).get(product, {}).get(duration, 0)
        old_price = float(current_price if current_price else default_price)
        new_price = max(0, old_price - 1)
        
        # Update database
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute('''
                    DELETE FROM prices 
                    WHERE seller_id = %s AND product = %s AND duration = %s
                ''', (int(seller_id), product, int(duration)))
                
                cur.execute('''
                    INSERT INTO prices (product, duration, seller_id, price)
                    VALUES (%s, %s, %s, %s)
                ''', (product, int(duration), int(seller_id), float(new_price)))
                
                conn.commit()
                print(f"✅ Price decreased: Seller {seller_id}, {product} {duration}d: {old_price} → {new_price}")
            except Exception as db_err:
                print(f"❌ DB Error: {db_err}")
                conn.rollback()
            finally:
                cur.close()
                conn.close()
        
        msg = f"✅ تم تقليل السعر!\n\n"
        msg += f"البائع: {seller_id}\n"
        msg += f"المنتج: {product}\n"
        msg += f"المدة: {duration} يوم\n"
        msg += f"${old_price} → ${new_price}"
        
        await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_quick_price")]]))
        return
    
    # Change seller prices - Step 2: Select Product
    if data and data.startswith("price_seller:"):
        seller_id = data.split(":")[1]
        products = list(PRICES.get("global", {}).keys())
        
        keyboard = []
        for prod in products:
            keyboard.append([InlineKeyboardButton(prod, callback_data=f"price_product:{seller_id}:{prod}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_change_seller_prices")])
        await query.edit_message_text(f"اختر المنتج للبائع {seller_id}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Change seller prices - Step 3: Select Duration
    if data and data.startswith("price_product:"):
        parts = data.split(":")
        seller_id = parts[1]
        product = parts[2]
        
        durations = list(PRICES.get("global", {}).get(product, {}).keys())
        keyboard = []
        for dur in durations:
            current_price = get_price(PRICES, product, dur, seller_id)
            default_price = PRICES.get("global", {}).get(product, {}).get(dur, 0)
            price_text = current_price if current_price else default_price
            keyboard.append([InlineKeyboardButton(f"{dur} يوم - ${price_text}", callback_data=f"price_duration:{seller_id}:{product}:{dur}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"price_seller:{seller_id}")])
        await query.edit_message_text(f"اختر المدة للمنتج {product}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Change seller prices - Step 4: Input Price
    if data and data.startswith("price_duration:"):
        parts = data.split(":")
        seller_id = parts[1]
        product = parts[2]
        duration = parts[3]
        
        context.user_data["admin_action"] = "change_seller_price"
        context.user_data["seller_id"] = seller_id
        context.user_data["product"] = product
        context.user_data["duration"] = duration
        
        await query.edit_message_text(f"أدخل السعر الجديد للمنتج {product} ({duration}يوم) للبائع {seller_id}:" + SIGNATURE)
        return
    
    # Seller design - Step 1: Select Seller
    if data == "admin_seller_design":
        sellers = DATA.get("sellers", {})
        if not sellers:
            await query.edit_message_text("لا يوجد بائعون" + SIGNATURE)
            return
        
        keyboard = []
        for sid, info in sellers.items():
            keyboard.append([InlineKeyboardButton(f"🎨 {info.get('name')}", callback_data=f"design_seller:{sid}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
        await query.edit_message_text("اختر البائع لتعديل تصميمه:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Seller design - Step 2: Choose option
    if data and data.startswith("design_seller:"):
        seller_id = data.split(":")[1]
        design = get_seller_design(seller_id)
        
        keyboard = [
            [InlineKeyboardButton("🎨 اللون", callback_data=f"design_color:{seller_id}")],
            [InlineKeyboardButton("📝 رسالة الترحيب", callback_data=f"design_welcome:{seller_id}")],
            [InlineKeyboardButton("🔘 نمط الأزرار", callback_data=f"design_buttons:{seller_id}")],
            [InlineKeyboardButton("📸 اللوجو", callback_data=f"design_logo:{seller_id}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="admin_seller_design")]
        ]
        
        current = "لا يوجد تصميم حالي"
        if design:
            current = f"اللون: {design['color']}\nالأزرار: {design['button_style']}"
        
        await query.edit_message_text(f"تعديل تصميم البائع {seller_id}:\n\n{current}" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Back button
    if data == "back_to_start":
        await start(update, context)
        return
    
    # Change language
    if data and data.startswith("set_lang:"):
        lang = data.split(":")[1]
        context.user_data["lang"] = lang
        await query.edit_message_text("✅ تم تغيير اللغة!" if lang == "ar" else "✅ Language changed!" + SIGNATURE)
        await start(update, context)
        return
    
    # Show Activity/Statistics
    if data == "show_activity":
        DATA = load_data()
        sellers = DATA.get("sellers", {})
        sales = DATA.get("sales_log", [])
        users = DATA.get("users", [])
        
        msg = f"📊 الإحصائيات:\n\n"
        msg += f"👥 عدد المستخدمين: {len(users)}\n"
        msg += f"👨‍💼 عدد البائعين: {len(sellers)}\n"
        msg += f"📦 عدد المبيعات: {len(sales)}\n\n"
        
        if sellers:
            msg += "📋 البائعون:\n"
            for sid, info in sellers.items():
                msg += f"• {info.get('name')} - رصيد: ${info.get('balance')} - مبيعات: {info.get('sales_count')}\n"
        
        await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
        return

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message.text else ""
    lang = context.user_data.get("lang", "ar")
    
    action = context.user_data.get("admin_action")
    
    # Handle main menu buttons
    if text == "🛍️ شراء مفاتيح" or text == "🛍️ BUY KEYS":
        PRICES = load_prices()
        products = list(PRICES.get("global", {}).keys())
        keyboard = []
        for prod in products:
            keyboard.append([InlineKeyboardButton(prod, callback_data=f"buy_product:{prod}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")])
        await update.message.reply_text("اختر المنتج:" if lang == "ar" else "Select a product:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    if text == "💰 رصيدي" or text == "💰 MY BALANCE":
        uid = str(update.message.from_user.id)
        DATA = load_data()
        balance = DATA.get("balances", {}).get(uid, 0)
        await update.message.reply_text(f"رصيدك: ${balance}" if lang == "ar" else f"Your balance: ${balance}")
        return
    
    if text == "🔐 لوحة الادمن" or text == "🔐 ADMIN PANEL":
        context.user_data["awaiting_admin_code"] = True
        await update.message.reply_text("أدخل كود الإدمن:" if lang == "ar" else "Enter admin code:")
        return
    
    if text == "🌐 تغيير اللغة" or text == "🌐 Change Language":
        keyboard = [
            [InlineKeyboardButton("العربية", callback_data="set_lang:ar")],
            [InlineKeyboardButton("English", callback_data="set_lang:en")]
        ]
        await update.message.reply_text("اختر اللغة / Select language:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    if text == "⬅️ Back":
        await start(update, context)
        return
    
    # Handle change seller price
    if action == "change_seller_price":
        try:
            seller_id = str(context.user_data.get("seller_id"))
            product = str(context.user_data.get("product"))
            duration = str(context.user_data.get("duration"))
            price = float(text)
            
            # Direct database insert
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                try:
                    cur.execute('''
                        DELETE FROM prices 
                        WHERE seller_id = %s AND product = %s AND duration = %s
                    ''', (int(seller_id), product, int(duration)))
                    
                    cur.execute('''
                        INSERT INTO prices (product, duration, seller_id, price)
                        VALUES (%s, %s, %s, %s)
                    ''', (product, int(duration), int(seller_id), float(price)))
                    
                    conn.commit()
                    print(f"✅ Price updated: Seller {seller_id}, Product {product}, Duration {duration}, Price {price}")
                except Exception as db_err:
                    print(f"❌ DB Error: {db_err}")
                    conn.rollback()
                finally:
                    cur.close()
                    conn.close()
            
            # Verify the price was saved
            prices_after = load_prices()
            saved_price = get_price(prices_after, product, duration, seller_id)
            
            msg = f"✅ تم تحديث السعر!\n\nالبائع: {seller_id}\nالمنتج: {product}\nالمدة: {duration} يوم\n"
            msg += f"السعر الجديد: ${price}\nالسعر المحفوظ: ${saved_price}"
            
            await update.message.reply_text(msg + SIGNATURE)
            context.user_data.pop("admin_action", None)
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}" + SIGNATURE)
        return
    
    # Handle admin add keys
    if action == "add_keys":
        product = context.user_data.get("add_keys_product")
        duration = context.user_data.get("add_keys_duration")
        
        keys = [k.strip() for k in text.split("\n") if k.strip()]
        if not keys:
            await update.message.reply_text("❌ لا توجد مفاتيح" + SIGNATURE)
            return
        
        add_keys_to_db(product, duration, keys)
        await update.message.reply_text(f"✅ تم إضافة {len(keys)} مفتاح" + SIGNATURE)
        context.user_data.pop("admin_action", None)
        return
    
    # Handle add balance
    if action == "add_balance":
        try:
            parts = text.split()
            uid, amount = parts[0], float(parts[1])
            DATA = load_data()
            DATA["balances"][uid] = DATA.get("balances", {}).get(uid, 0) + amount
            save_data(DATA)
            await update.message.reply_text(f"✅ تم إضافة ${amount} للمستخدم {uid}\nالرصيد الجديد: ${DATA['balances'][uid]}" + SIGNATURE)
            context.user_data.pop("admin_action", None)
        except:
            await update.message.reply_text("❌ صيغة خاطئة! أدخل: user_id amount" + SIGNATURE)
        return
    
    # Handle admin code
    if context.user_data.get("awaiting_admin_code"):
        if text == ADMIN_CODE:
            context.user_data.pop("awaiting_admin_code", None)
            await update.message.reply_text("✅ مرحباً الأدمن!" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("لوحة التحكم", callback_data="admin_menu")]]))
        else:
            await update.message.reply_text("❌ الكود خاطئ" + SIGNATURE)
        return

# ========== MAIN ==========
def main():
    if not TOKEN:
        print("❌ ERROR: TOKEN_BOT_2 environment variable not set!")
        print("\nHow to fix:")
        print("1. Go to Render Dashboard")
        print("2. Select your service")
        print("3. Go to 'Environment' tab")
        print("4. Add: TOKEN_BOT_2 = your_real_bot_token")
        print("5. Redeploy the service")
        sys.exit(1)
    
    print(f"✅ Bot token loaded successfully")
    print(f"✅ Admin code: {ADMIN_CODE}")
    print(f"✅ Database: {DATABASE_URL[:50]}...")
    
    init_db()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("✅ Bot 2 starting...")
    try:
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
