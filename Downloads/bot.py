import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InputFile
import telegram
import os
from datetime import datetime
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import sqlite3

# Read from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CODE = os.getenv("ADMIN_CODE", "123123NNK")
SIGNATURE = "\n\n© @FAKHERDDIN5"
SELLER_CHANNEL_URL = "https://t.me/stonexff"
DB_PATH = os.getenv("DB_PATH", "bot.db")

# Database connection
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        # If database is corrupted, remove it and create a new one
        if "file is not a database" in str(e):
            print(f"🔧 Removing corrupted database: {DB_PATH}")
            try:
                os.remove(DB_PATH)
                print("✅ Creating new database...")
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                return conn
            except Exception as remove_error:
                print(f"Failed to remove corrupted database: {remove_error}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sellers table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sellers (
                seller_id INTEGER PRIMARY KEY,
                name TEXT,
                balance REAL DEFAULT 0,
                sales_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Keys table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS keys (
                key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT,
                duration INTEGER,
                key_value TEXT UNIQUE,
                is_used BOOLEAN DEFAULT 0,
                sold_to INTEGER,
                sold_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Prices table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                price_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT,
                duration INTEGER,
                seller_id INTEGER,
                price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sales log table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sales_log (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER,
                product TEXT,
                duration INTEGER,
                qty INTEGER,
                unit_price REAL,
                total_price REAL,
                seller_id INTEGER,
                buyer_balance REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Stats table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_clicks INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ensure stats row exists
        cur.execute('INSERT OR IGNORE INTO stats (stat_id, start_clicks) VALUES (1, 0)')
        
        conn.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
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
    
    cur = conn.cursor()
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
        cur.execute('SELECT start_clicks FROM stats WHERE stat_id = 1')
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
                INSERT OR REPLACE INTO users (user_id, balance)
                VALUES (?, ?)
            ''', (int(uid), balance))
        
        # Update sellers
        for sid, info in data.get("sellers", {}).items():
            cur.execute('''
                INSERT OR REPLACE INTO sellers (seller_id, name, balance, sales_count)
                VALUES (?, ?, ?, ?)
            ''', (int(sid), info.get("name"), info.get("balance", 0), info.get("sales_count", 0)))
        
        # Update start_clicks
        cur.execute('UPDATE stats SET start_clicks = ? WHERE stat_id = 1', 
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
    
    cur = conn.cursor()
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
                    VALUES (?, ?, ?)
                ''', (product, int(duration), price))
        
        # Save seller prices
        for seller_id, products in prices.get("sellers", {}).items():
            for product, durations in products.items():
                for duration, price in durations.items():
                    cur.execute('''
                        INSERT INTO prices (product, duration, seller_id, price)
                        VALUES (?, ?, ?, ?)
                    ''', (product, int(duration), int(seller_id), price))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving prices: {e}")
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
                INSERT OR IGNORE INTO keys (product, duration, key_value)
                VALUES (?, ?, ?)
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
    
    cur = conn.cursor()
    keys = []
    try:
        cur.execute('''
            SELECT key_id, key_value FROM keys 
            WHERE product = ? AND duration = ? AND is_used = 0 
            LIMIT ?
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
                UPDATE keys SET is_used = 1, sold_to = ?, sold_at = CURRENT_TIMESTAMP
                WHERE key_value = ?
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (int(buyer_id), product, int(duration), qty, unit_price, total_price, 
              int(seller_id) if seller_id else None, buyer_balance))
        conn.commit()
    except Exception as e:
        print(f"Error logging sale: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def get_uid_from_update(update: Update):
  try:
      if getattr(update, "message", None) and update.message.from_user:
          return str(update.message.from_user.id)
      if getattr(update, "callback_query", None) and update.callback_query.from_user:
          return str(update.callback_query.from_user.id)
  except Exception:
      return None


def get_price(prices, product, duration, seller_id=None):
  duration = str(duration)
  if seller_id:
      seller_prices = prices.get("sellers", {}).get(seller_id, {})
      if product in seller_prices and duration in seller_prices[product]:
          return seller_prices[product][duration]
  return prices.get("global", {}).get(product, {}).get(duration)


# Minimal /start handler to fix NameError at startup
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  lang = context.user_data.get("lang", "en")
  button_texts = {
      "buy": {"en": "🛍️ BUY KEYS", "ar": "🛍️ شراء مفاتيح"},
      "balance": {"en": "💰 MY BALANCE", "ar": "💰 رصيدي"},
      "admin": {"en": "🔐 ADMIN PANEL", "ar": "🔐 لوحة الادمن"},
      "lang": {"en": "🌐 Change Language", "ar": "🌐 تغيير اللغة"},
      "get_files": {"en": "📁 Get Files", "ar": "📁 الحصول على الملفات"}
  }
  # if caller is a seller, show Get Files button
  uid = None
  try:
      if getattr(update, "message", None):
          uid = str(update.message.from_user.id)
      elif getattr(update, "callback_query", None):
          uid = str(update.callback_query.from_user.id)
  except Exception:
      uid = None
  DATA_START = load_data()
  reply_keyboard = [[button_texts["buy"][lang]], [button_texts["balance"][lang]],[button_texts["admin"][lang]]]
  # always offer Get Files — customers who purchased will see their products
  reply_keyboard.append([button_texts["get_files"][lang]])
  reply_keyboard.append([button_texts["lang"][lang]])
  reply_keyboard.append(["⬅️ Back"])
  text = "Welcome to the Sales Bot! Please choose an option:" if lang == "en" else "مرحباً بك في بوت المبيعات! اختر خياراً:"
  # Use reply_text when invoked by command, or reply when invoked via callback
  if getattr(update, "message", None):
      # increment start click counter
      try:
          DATA_START["start_clicks"] = DATA_START.get("start_clicks", 0) + 1
          save_data(DATA_START)
      except Exception:
          pass
      await update.message.reply_text(text + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      # one-time seller promo for non-sellers
      try:
          uid_str = uid
          if uid_str and uid_str not in DATA_START.get("sellers", {}) and uid_str not in DATA_START.get("seller_promo_shown", []):
              promo = "Become a seller — deposit just $30 one time to start selling. Join our channel for details:"
              kb = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=SELLER_CHANNEL_URL), InlineKeyboardButton("Dismiss", callback_data="dismiss_seller_promo")]])
              await update.message.reply_text(promo + SIGNATURE, reply_markup=kb)
              DATA_START.setdefault("seller_promo_shown", []).append(uid_str)
              save_data(DATA_START)
      except Exception:
          pass
  elif getattr(update, "callback_query", None):
      try:
          DATA_START["start_clicks"] = DATA_START.get("start_clicks", 0) + 1
          save_data(DATA_START)
      except Exception:
          pass
      await update.callback_query.message.reply_text(text + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      # one-time seller promo for non-sellers when started via callback
      try:
          uid_str = uid
          if uid_str and uid_str not in DATA_START.get("sellers", {}) and uid_str not in DATA_START.get("seller_promo_shown", []):
              promo = "Become a seller — deposit just $30 one time to start selling. Join our channel for details:"
              kb = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=SELLER_CHANNEL_URL), InlineKeyboardButton("Dismiss", callback_data="dismiss_seller_promo")]])
              await update.callback_query.message.reply_text(promo + SIGNATURE, reply_markup=kb)
              DATA_START.setdefault("seller_promo_shown", []).append(uid_str)
              save_data(DATA_START)
      except Exception:
          pass


# ========== CALLBACK HANDLER ==========
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  # Activity is only available in the admin area (handled via callbacks)
  try:
      await query.answer()
  except telegram.error.BadRequest as e:
      if 'Query is too old' in str(e) or 'query id is invalid' in str(e):
          # Ignore expired/invalid callback queries
          return
      else:
          print(f"CallbackQuery answer error: {e}")
          return
  except Exception as e:
      print(f"CallbackQuery answer unexpected error: {e}")
      return
  data = getattr(query, "data", None)
  DATA = load_data()
  PRICES = load_prices()
 

  # Back / main menu
  if data == "back_to_start":
      lang = context.user_data.get("lang", "en")
      menu_text = "Welcome to the Sales Bot! Please choose an option:" if lang == "en" else "مرحباً بك في بوت المبيعات! اختر خياراً:"
      reply_keyboard = [["🛍️ BUY KEYS" if lang == "en" else "🛍️ شراء مفاتيح"], ["💰 MY BALANCE" if lang == "en" else "💰 رصيدي"], ["🔐 ADMIN PANEL" if lang == "en" else "🔐 لوحة الادمن"], ["🌐 Change Language" if lang == "en" else "🌐 تغيير اللغة"], ["⬅️ Back"]]
      # reset interaction state but preserve language
      lang_val = context.user_data.get("lang")
      context.user_data.clear()
      if lang_val:
          context.user_data["lang"] = lang_val
      await query.edit_message_text(menu_text + SIGNATURE)
      # send reply keyboard for main menu
      await query.message.reply_text(menu_text + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      return

  # Admin Main Menu

  if data == "admin_menu":
      admin_keyboard = [
          [InlineKeyboardButton("💳 Add Balance", callback_data="admin_add_balance")],
          [InlineKeyboardButton("💸 Withdraw", callback_data="admin_withdraw")],
          [InlineKeyboardButton("🔑 Add Keys", callback_data="admin_add_keys")],
          [InlineKeyboardButton("➕ Add Seller", callback_data="admin_add_seller_cb")],
          [InlineKeyboardButton("➖ Remove Seller", callback_data="admin_remove_seller_cb")],
          [InlineKeyboardButton("📋 List Sellers", callback_data="admin_list_sellers")],
          [InlineKeyboardButton("💰 Sellers Balance", callback_data="admin_sellers")],
          [InlineKeyboardButton("� Change Seller Prices", callback_data="admin_change_seller_prices")],
          [InlineKeyboardButton("�🔑 Available Keys", callback_data="admin_available_keys")],
          [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
          [InlineKeyboardButton("📝 آخر عمليات الشراء", callback_data="admin_last_sales")],
          [InlineKeyboardButton("📊 Activity", callback_data="show_activity")],
          [InlineKeyboardButton("🧾 جميع أرصدة اللاعبين", callback_data="admin_all_balances")],
          [InlineKeyboardButton("🗝️ سحب المفاتيح", callback_data="admin_withdraw_keys")],
          [InlineKeyboardButton("🗂️ جميع المفاتيح والعوائد", callback_data="admin_keys_revenue")],
          [InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]
      ]
      await query.edit_message_text("قائمة الأدمن:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(admin_keyboard))
      return
  # Show all player balances
  if data == "admin_all_balances":
      DATA = load_data()
      balances = DATA.get("balances", {})
      users = DATA.get("users", [])
      msg = "🧾 جميع أرصدة اللاعبين:\n\n"
      for uid in users:
          bal = balances.get(uid, 0)
          msg += f"• {uid}: ${bal}\n"
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Withdraw keys (admin)
  if data == "admin_withdraw_keys":
      context.user_data.clear()
      context.user_data["admin_action"] = "withdraw_keys"
      await query.edit_message_text("أدخل اسم المنتج والمدة وعدد المفاتيح للسحب (مثال: FREE 7 2)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Show all keys (sold/unsold) and revenue
  if data == "admin_keys_revenue":
      DATA = load_data()
      PRICES = load_prices()
      keys_data = DATA.get("keys", {})
      used_keys = set(DATA.get("used_keys", []))
      sales_log = DATA.get("sales_log", [])
      msg = "🗂️ جميع المفاتيح:\n\n"
      total_revenue = 0
      for prod_dur, keys in keys_data.items():
          sold = [k for k in keys if k in used_keys]
          unsold = [k for k in keys if k not in used_keys]
          msg += f"{prod_dur}:\n  المباعة: {len(sold)}\n  الغير مباعة: {len(unsold)}\n"
      # Revenue calculation
      for sale in sales_log:
          try:
              total_revenue += float(sale.get("price", 0))
          except Exception:
              pass
      msg += f"\n💵 مجموع العوائد: ${total_revenue}"
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Show last 10 sales to admin
  if data == "admin_last_sales":
      sales = DATA.get("sales_log", [])[-10:]
      sellers = DATA.get("sellers", {})
      if not sales:
          await query.edit_message_text("لا توجد عمليات شراء بعد." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      msg = "📝 آخر عمليات الشراء:\n\n"
      for s in reversed(sales):
          seller_id = s.get('seller_id')
          seller_name = sellers.get(seller_id, {}).get('name', '?') if seller_id else 'غير محدد'
          msg += f"المنتج: {s.get('product','?')}\nالمدة: {s.get('duration','?')}\nرصيد المشتري بعد الشراء: ${s.get('buyer_balance','?')}\nالبائع: {seller_name}\n---\n"
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Show available keys for each product/duration
      # Show last 10 sales to admin
      if data == "admin_last_sales":
          sales = DATA.get("sales_log", [])[-10:]
          if not sales:
              await query.edit_message_text("لا توجد عمليات شراء بعد." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
              return
          msg = "📝 آخر عمليات الشراء:\n\n"
          for s in reversed(sales):
              msg += f"المنتج: {s.get('product','?')}\nالمدة: {s.get('duration','?')}\nرصيد المشتري بعد الشراء: ${s.get('buyer_balance','?')}\n---\n"
          await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
  if data == "admin_available_keys":
      keys_data = DATA.get("keys", {})
      used_keys = set(DATA.get("used_keys", []))
      if not keys_data:
          await query.edit_message_text("لا توجد أي مفاتيح متوفرة حالياً." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      msg = "🔑 المفاتيح المتوفرة:\n\n"
      for prod_dur, keys in keys_data.items():
          available = [k for k in keys if k not in used_keys]
          msg += f"{prod_dur}: {len(available)} مفتاح متوفر\n"
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # List all sellers with balances
  if data == "admin_list_sellers":
      DATA = load_data()
      sellers = DATA.get("sellers", {})
      balances = DATA.get("balances", {})
      if not sellers:
          await query.edit_message_text("لا يوجد بائعون مضافون بعد." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      msg = "\U0001F4CB قائمة البائعين مع الرصيد:\n\n"
      for sid, info in sellers.items():
          real_balance = balances.get(sid, info.get('balance', 0))
          msg += f"• {info.get('name','?')} (ID: {sid})\n  Balance: ${real_balance} | Sales: {info.get('sales_count',0)}\n\n"
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Broadcast message to all users
  if data == "admin_broadcast":
      context.user_data["admin_action"] = "broadcast"
      await query.edit_message_text("أرسل الرسالة التي تريد إرسالها لجميع المستخدمين:" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Add Seller
  if data == "admin_add_seller_cb":
      context.user_data.clear()
      context.user_data["admin_action"] = "add_seller"
      await query.edit_message_text("أدخل معرف البائع والاسم (مثال: 123456789 @sellername)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Remove Seller
  if data == "admin_remove_seller_cb":
      context.user_data.clear()
      context.user_data["admin_action"] = "remove_seller"
      await query.edit_message_text("أدخل معرف البائع للحذف (مثال: 123456789)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Toggle Seller Work (placeholder)
  if data == "admin_toggle_seller_work":
      await query.edit_message_text("(ميزة قيد التطوير: تبديل حالة عمل البائعين)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Buy menu
  if data == "buy_menu":
      lang = context.user_data.get("lang", "en")
      product_names = {
          "FREE": {"en": "🔮 FREE FIRE", "ar": "🔮 فري فاير"},
          "WIZARD": {"en": "✨ WIZARD", "ar": "✨ ويزارد"},
          "DRIP": {"en": "💧 DRIP", "ar": "💧 دريب"},
          "CERT": {"en": "🎖️ CERTIFICATE", "ar": "🎖️ شهادة"},
          "CLOUD": {"en": "☁️ CLOUD", "ar": "☁️ كلاود"},
          "CODM_IOS": {"en": "📱 CODM IOS", "ar": "📱 كودم IOS"},
          "TERMINAL_X_PC": {"en": "💻 TERMINAL X PC", "ar": "💻 تيرمنال X PC"},
          "HG_CHEATS_ROOT": {"en": "🛡️ HG CHEATS ROOT", "ar": "🛡️ HG شيتس روت"}
      }
      reply_keyboard = [[product_names[p][lang]] for p in product_names]
      reply_keyboard.append(["⬅️ Back"])
      # mark that user is in buy menu so reply-keyboard selections are processed
      context.user_data["buy_menu"] = True
      await query.edit_message_text("اختر المنتج:" + SIGNATURE)
      await query.message.reply_text("اختر المنتج:" + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      return

  if data == "show_balance":
      user_id = str(query.from_user.id)
      bal = DATA.get("balances", {}).get(user_id, 0)
      keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]
      await query.edit_message_text(f"Your balance: ${bal}" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  # Activity / statistics
  if data == "show_activity":
      DATA_STAT = load_data()
      uid = str(query.from_user.id)
      # only admins and sellers can view activity
      admins = set(DATA_STAT.get("admins", []))
      sellers_map = DATA_STAT.get("sellers", {})
      if uid not in admins and uid not in sellers_map:
          await query.edit_message_text("❌ Permission denied. Activity is for admins and sellers only." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
          return

      # Seller view: show seller balance and their sales
      if uid in sellers_map:
          seller = sellers_map.get(uid, {})
          balance = seller.get("balance", 0)
          sales = [s for s in DATA_STAT.get("sales_log", []) if s.get("seller_id") == uid]
          sold_count = len(sales)
          by_product = {}
          for s in sales:
              by_product[s.get("product")] = by_product.get(s.get("product"), 0) + 1
          msg = f"📊 Seller Activity ({seller.get('name','Unknown')} - {uid}):\n\nBalance: ${balance}\nKeys sold: {sold_count}\n\nSold by product:\n"
          if by_product:
              for p, c in by_product.items():
                  msg += f"- {p}: {c}\n"
          else:
              msg += "(no sales yet)\n"
          keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]
          await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
          return

      # Admin view: overall stats + per-seller breakdown
      start_clicks = DATA_STAT.get("start_clicks", 0)
      users_count = len(DATA_STAT.get("users", []))
      used_keys = DATA_STAT.get("used_keys", []) or []
      total_keys_sold = len(used_keys)
      total_keys_available = sum(len(v) for v in DATA_STAT.get("keys", {}).values())
      sellers = DATA_STAT.get("sellers", {})
      sellers_count = len(sellers)
      sales_count = len(DATA_STAT.get("sales_log", []))
      sold_by_product = {}
      for s in DATA_STAT.get("sales_log", []):
          sold_by_product[s.get("product")] = sold_by_product.get(s.get("product"), 0) + 1
      msg = f"📊 Bot Activity Summary:\n\nStart clicks: {start_clicks}\nKnown users: {users_count}\nTotal sales entries: {sales_count}\nKeys sold: {total_keys_sold}\nKeys available: {total_keys_available}\nSellers: {sellers_count}\n\nSold by product:\n"
      for prod, cnt in sold_by_product.items():
          msg += f"- {prod}: {cnt}\n"
      msg += "\nPer-seller breakdown:\n"
      if sellers:
          for sid, info in sellers.items():
              s_sales = [s for s in DATA_STAT.get("sales_log", []) if s.get("seller_id") == sid]
              s_count = len(s_sales)
              prod_counts = {}
              for s in s_sales:
                  prod_counts[s.get("product")] = prod_counts.get(s.get("product"), 0) + 1
              msg += f"- {info.get('name','?')} ({sid}) — Balance: ${info.get('balance',0)} — Keys sold: {s_count}\n"
              if prod_counts:
                  for p, c in prod_counts.items():
                      msg += f"    • {p}: {c}\n"
      else:
          msg += "(no sellers configured)\n"

      keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  # Dismiss seller promo
  if data == "dismiss_seller_promo":
      try:
          await query.edit_message_text("Promo dismissed." + SIGNATURE)
      except Exception:
          pass
      return

  # Buy flow: show durations
  if data and data.startswith("buy:"):
      product = data.split(":", 1)[1]
      user_id = str(query.from_user.id)
      show_prices = user_id in DATA.get("balances", {})
      prod_prices = PRICES.get("global", {}).get(product)
      if not prod_prices:
          await query.edit_message_text(f"⚠️ No pricing/config found for {product}. Ask the admin to set prices or add keys." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="buy_menu")]]))
          return
      keyboard = []
      for days, price in sorted(prod_prices.items(), key=lambda x: int(x[0])):
          btn_text = f"⏱️ {days}يوم - ${price}" if show_prices else f"⏱️ {days}يوم"
          keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"choose_qty:{product}:{days}")])
      keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="buy_menu")])
      if show_prices:
          await query.edit_message_text(f"اختر المدة للمنتج {product}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      else:
          await query.edit_message_text(f"اختر المدة للمنتج {product}:\n(سيتم عرض الأسعار بعد إضافتك من قبل الأدمن)" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  # Choose quantity
  if data and data.startswith("choose_qty:"):
      _, product, days = data.split(":", 2)
      qty_keyboard = [[InlineKeyboardButton(str(i), callback_data=f"pay:{product}:{days}:{i}")] for i in range(1, 11)]
      qty_keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"buy:{product}")])
      await query.edit_message_text(f"Select quantity for {product} ({days} days):" + SIGNATURE, reply_markup=InlineKeyboardMarkup(qty_keyboard))
      return

  # Pay / complete purchase (notify admins)
  if data and data.startswith("pay:"):
      parts = data.split(":")
      product = parts[1]
      days = str(parts[2])  # تحويل إلى string
      qty = int(parts[3]) if len(parts) > 3 else 1

      user_id = str(query.from_user.id)

      DATA = load_data()
      PRICES = load_prices()

      # إذا كان المستخدم بائع → يستعمل سعره الخاص
      seller_id = user_id if user_id in DATA.get("sellers", {}) else None

      # السعر الصحيح (سعر البائع إن وجد – وإلا السعر العام)
      unit_price = get_price(PRICES, product, days, seller_id)
      if unit_price is None:
          await query.edit_message_text(
              f"⚠️ لا يوجد سعر لهذا المنتج {product} لمدة {days} يوم."
              + SIGNATURE
          )
          return

      total_price = unit_price * qty
      balance = float(DATA.get("balances", {}).get(user_id, 0))

      if balance < total_price:
          await query.edit_message_text(
              f"❌ الرصيد غير كافٍ\n"
              f"السعر: ${total_price}\n"
              f"رصيدك: ${balance}"
              + SIGNATURE
          )
          return

      # Get available keys from database
      sold_keys = get_available_keys(product, days, qty)
      
      if len(sold_keys) < qty:
          await query.edit_message_text(
              "❌ لا يوجد عدد كافٍ من المفاتيح."
              + SIGNATURE
          )
          return

      # Mark keys as used in database
      mark_keys_used(sold_keys, user_id)

      # خصم الرصيد
      DATA["balances"][user_id] = balance - total_price

      # تسجيل البيع
      log_sale(user_id, product, days, qty, unit_price, total_price, seller_id, DATA["balances"][user_id])
      
      save_data(DATA)

      keys_text = "\n".join([f"`{k}`" for k in sold_keys])

      await query.edit_message_text(
          f"✅ تم الشراء بنجاح\n\n"
          f"السعر للوحدة: ${unit_price}\n"
          f"السعر الكلي: ${total_price}\n\n"
          f"🔑 مفاتيحك:\n{keys_text}"
          + SIGNATURE,
          parse_mode="Markdown"
      )
      return

  # Admin login
  if data == "admin_add_keys":
      PRICES = load_prices()
      keyboard = [[InlineKeyboardButton(prod, callback_data=f"admin_add_keys_product:{prod}")] for prod in PRICES.get("global", {}).keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("اختر المنتج لإضافة المفاتيح:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_add_keys_product:"):
      _, prod = data.split(":", 1)
      PRICES = load_prices()
      durations = list(PRICES.get("global", {}).get(prod, {}).keys())
      if not durations:
          await query.edit_message_text(f"لا يوجد مدد معرفة لهذا المنتج {prod}. أضف مدد أولاً من الأسعار." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")]]))
          return
      keyboard = [[InlineKeyboardButton(f"{d} يوم", callback_data=f"admin_add_keys_duration:{prod}:{d}")] for d in durations]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")])
      await query.edit_message_text(f"اختر المدة لإضافة المفاتيح لـ {prod}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_add_keys_duration:"):
      _, prod, days = data.split(":", 2)
      context.user_data.clear()
      context.user_data["admin_action"] = "add_keys"
      context.user_data["add_keys_product"] = prod
      context.user_data["add_keys_duration"] = days
      await query.edit_message_text(f"أرسل المفاتيح (كل مفتاح في سطر) ليتم إضافتها للمنتج {prod} لمدة {days} يوم." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")]]))
      return
      await query.edit_message_text("قائمة الأدمن:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  # Admin: Download all keys as text file
  if data == "admin_download_keys":
      import tempfile
      DATA = load_data()
      keys_data = DATA.get("keys", {})
      used_keys = set(DATA.get("used_keys", []))
      lines = []
      for prod_dur, keys in keys_data.items():
          available = [k for k in keys if k not in used_keys]
          lines.append(f"{prod_dur}:")
          if available:
              for k in available:
                  lines.append(f"- {k}")
          else:
              lines.append("(لا يوجد مفاتيح متاحة)")
          lines.append("")
      content = "\n".join(lines)
      with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix="_keys.txt") as tf:
          tf.write(content)
          temp_path = tf.name
      await context.bot.send_document(chat_id=query.from_user.id, document=InputFile(temp_path), filename="all_keys.txt", caption="جميع المفاتيح المتوفرة")
      import os
      try:
          os.remove(temp_path)
      except Exception:
          pass
      await query.edit_message_text("تم إرسال ملف جميع المفاتيح المتوفرة لك." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Admin: View all keys for all products
  if data == "admin_view_keys":
      DATA = load_data()
      keys_data = DATA.get("keys", {})
      used_keys = set(DATA.get("used_keys", []))
      if not keys_data:
          await query.edit_message_text("لا توجد أي مفاتيح متوفرة حالياً." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      msg = "🔍 جميع المفاتيح المتوفرة:\n\n"
      for prod_dur, keys in keys_data.items():
          available = [k for k in keys if k not in used_keys]
          msg += f"{prod_dur}:\n"
          if available:
              for k in available:
                  msg += f"- `{k}`\n"
          else:
              msg += "(لا يوجد مفاتيح متاحة)\n"
          msg += "\n"
      await query.edit_message_text(msg + SIGNATURE, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Admin: show product list to edit per-seller prices
  if data == "admin_edit_prices":
      PRICES = load_prices()
      keyboard = [[InlineKeyboardButton(prod, callback_data=f"edit_price:{prod}")] for prod in PRICES.get("global", {}).keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Select product to edit prices for:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("edit_price:"):
      _, prod = data.split(":", 1)
      PRICES = load_prices()
      prod_prices = PRICES.get("global", {}).get(prod, {})
      if not prod_prices:
          await query.edit_message_text("No price durations configured for this product." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_edit_prices")]]))
          return
      keyboard = [[InlineKeyboardButton(f"{days} days", callback_data=f"edit_price_choose_days:{prod}:{days}")] for days in prod_prices.keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_edit_prices")])
      await query.edit_message_text(f"Select duration for {prod}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("edit_price_choose_days:"):
      _, prod, days = data.split(":", 2)
      DATA = load_data()
      sellers = DATA.get("sellers", {})
      DATA_STAT = load_data()
      uid = str(query.from_user.id)
      admins = set(DATA_STAT.get("admins", []))
      sellers_map = DATA_STAT.get("sellers", {})
      if uid not in admins and uid not in sellers_map:
          await query.edit_message_text("❌ Permission denied. Activity is for admins and sellers only." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
          return

      # Seller view: show seller balance and their sales
      if uid in sellers_map:
          seller = sellers_map.get(uid, {})
          balance = seller.get("balance", 0)
          sales = [s for s in DATA_STAT.get("sales_log", []) if s.get("seller_id") == uid]
          sold_count = len(sales)
          by_product = {}
          for s in sales:
              by_product[s.get("product")] = by_product.get(s.get("product"), 0) + 1
          msg = f"📊 Seller Activity ({seller.get('name','Unknown')} - {uid}):\n\nBalance: ${balance}\nKeys sold: {sold_count}\n\nSold by product:\n"
          if by_product:
              for p, c in by_product.items():
                  msg += f"- {p}: {c}\n"
          else:
              msg += "(no sales yet)\n"
          keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]
          await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
          return

      # Admin view: overall stats + per-seller breakdown + all users (usernames)
      start_clicks = DATA_STAT.get("start_clicks", 0)
      users_list = DATA_STAT.get("users", [])
      users_names = []
      # Attempt to get usernames from sellers, else just show id with @
      for uid in users_list:
          name = None
          if uid in DATA_STAT.get("sellers", {}):
              name = DATA_STAT["sellers"][uid].get("name")
          if name and name.startswith("@"):  # username
              users_names.append(name)
          else:
              users_names.append(f"@{uid}")
      users_count = len(users_list)
      used_keys = DATA_STAT.get("used_keys", []) or []
      total_keys_sold = len(used_keys)
      total_keys_available = sum(len(v) for v in DATA_STAT.get("keys", {}).values())
      sellers = DATA_STAT.get("sellers", {})
      sellers_count = len(sellers)
      sales_count = len(DATA_STAT.get("sales_log", []))
      sold_by_product = {}
      for s in DATA_STAT.get("sales_log", []):
          sold_by_product[s.get("product")] = sold_by_product.get(s.get("product"), 0) + 1
      msg = f"📊 Bot Activity Summary:\n\nStart clicks: {start_clicks}\nKnown users: {users_count}\nTotal sales entries: {sales_count}\nKeys sold: {total_keys_sold}\nKeys available: {total_keys_available}\nSellers: {sellers_count}\n\nUsers who clicked /start (usernames or ids):\n"
      msg += "\n".join(users_names) + "\n\n"
      msg += "Sold by product:\n"
      for prod, cnt in sold_by_product.items():
          msg += f"- {prod}: {cnt}\n"
      msg += "\nPer-seller breakdown:\n"
      if sellers:
          for sid, info in sellers.items():
              s_sales = [s for s in DATA_STAT.get("sales_log", []) if s.get("seller_id") == sid]
              s_count = len(s_sales)
              prod_counts = {}
              for s in s_sales:
                  prod_counts[s.get("product")] = prod_counts.get(s.get("product"), 0) + 1
              msg += f"- {info.get('name','?')} ({sid}) — Balance: ${info.get('balance',0)} — Keys sold: {s_count}\n"
              if prod_counts:
                  for p, c in prod_counts.items():
                      msg += f"    • {p}: {c}\n"
      else:
          msg += "(no sellers configured)\n"

      keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return
  if data == "admin_create_key":
      PRICES = load_prices()
      keyboard = [[InlineKeyboardButton(prod, callback_data=f"admin_create_key_product:{prod}")] for prod in PRICES.get("global", {}).keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Select product to create a single key for:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return
  if data and data.startswith("admin_create_key_product:"):
      _, prod = data.split(":", 1)
      PRICES = load_prices()
      durations = list(PRICES.get("global", {}).get(prod, {}).keys())
      if not durations:
          await query.edit_message_text(f"No durations configured for {prod}. Add durations in prices first." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_create_key")]]))
          return
      keyboard = [[InlineKeyboardButton(f"{d} days", callback_data=f"admin_create_key_duration:{prod}:{d}")] for d in durations]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text(f"Select duration for new key for {prod}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_create_key_duration:"):
      _, prod, days = data.split(":", 2)
      context.user_data["admin_action"] = "create_key"
      context.user_data["create_key_product"] = prod
      context.user_data["create_key_duration"] = days
      await query.edit_message_text(f"Send the key string to create for product {prod} ({days} days)." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  # Admin: show sellers list with balances
  if data == "admin_sellers":
      DATA = load_data()
      sellers = DATA.get("sellers", {})
      if not sellers:
          await query.edit_message_text("No sellers configured." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      keyboard = []
      for sid, info in sellers.items():
          keyboard.append([InlineKeyboardButton(f"{info.get('name','?')} - {sid} - ${info.get('balance',0)}", callback_data=f"admin_seller:{sid}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Sellers:", reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_seller:"):
      _, sid = data.split(":", 1)
      DATA = load_data()
      s = DATA.get("sellers", {}).get(sid)
      if not s:
          await query.edit_message_text("Seller not found." + SIGNATURE)
          return
      keyboard = [[InlineKeyboardButton("Add Balance", callback_data=f"admin_add_seller_balance:{sid}")], [InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]
      await query.edit_message_text(f"Seller {s.get('name')} (ID: {sid})\nBalance: ${s.get('balance',0)}\nSales: {s.get('sales_count',0)}" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_add_seller_balance:"):
      _, sid = data.split(":", 1)
      context.user_data["admin_action"] = "add_seller_balance"
      context.user_data["target_seller"] = sid
      await query.edit_message_text(f"Send amount to add to seller {sid}:" + SIGNATURE)
      return

  # Admin: Change Seller Prices - Step 1: Select Seller
  if data == "admin_change_seller_prices":
      DATA = load_data()
      sellers = DATA.get("sellers", {})
      if not sellers:
          await query.edit_message_text("No sellers configured." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      keyboard = []
      for sid, info in sellers.items():
          keyboard.append([InlineKeyboardButton(f"{info.get('name','?')} ({sid})", callback_data=f"admin_select_seller_price:{sid}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Select seller to change their prices:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  # Admin: Change Seller Prices - Step 2: Select Product
  if data and data.startswith("admin_select_seller_price:"):
      _, seller_id = data.split(":", 1)
      PRICES = load_prices()
      products = PRICES.get("global", {}).keys()
      if not products:
          await query.edit_message_text("No products configured." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_change_seller_prices")]]))
          return
      keyboard = []
      for prod in products:
          keyboard.append([InlineKeyboardButton(prod, callback_data=f"admin_seller_edit_product:{seller_id}:{prod}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_change_seller_prices")])
      await query.edit_message_text(f"Select product for seller {seller_id}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  # Admin: Change Seller Prices - Step 3: Select Duration
  if data and data.startswith("admin_seller_edit_product:"):
      parts = data.split(":", 2)
      seller_id = parts[1]
      product = parts[2]
      PRICES = load_prices()
      durations = PRICES.get("global", {}).get(product, {})
      if not durations:
          await query.edit_message_text(f"No durations configured for {product}." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=f"admin_select_seller_price:{seller_id}")]]))
          return
      keyboard = []
      for duration in durations.keys():
          current_price = get_price(PRICES, product, duration, seller_id)
          default_price = PRICES.get("global", {}).get(product, {}).get(duration)
          keyboard.append([InlineKeyboardButton(f"{duration}d - Current: ${current_price if current_price else default_price}", callback_data=f"admin_seller_edit_price:{seller_id}:{product}:{duration}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"admin_select_seller_price:{seller_id}")])
      await query.edit_message_text(f"Select duration for {product} (seller {seller_id}):" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  # Admin: Change Seller Prices - Step 4: Input New Price
  if data and data.startswith("admin_seller_edit_price:"):
      parts = data.split(":", 3)
      seller_id = parts[1]
      product = parts[2]
      duration = parts[3]
      context.user_data["admin_action"] = "admin_set_seller_price"
      context.user_data["seller_id"] = seller_id
      context.user_data["product"] = product
      context.user_data["duration"] = duration
      PRICES = load_prices()
      current_price = get_price(PRICES, product, duration, seller_id)
      default_price = PRICES.get("global", {}).get(product, {}).get(duration)
      await query.edit_message_text(f"Current price for {product} ({duration}d):\n- Default: ${default_price}\n- Seller {seller_id}: ${current_price if current_price else 'Not Set'}\n\nSend new price for this seller:" + SIGNATURE)
      return

  # Admin broadcast
  if data == "admin_broadcast":
      context.user_data["admin_action"] = "broadcast"
      await query.edit_message_text("Send the broadcast message to deliver to all known users:" + SIGNATURE)
      return

  # Admin add file: choose product
  if data == "admin_add_balance":
      context.user_data.clear()
      context.user_data["admin_action"] = "add_balance"
      await query.edit_message_text("أدخل معرف المستخدم والمبلغ (مثال: 123456789 10)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if data == "admin_withdraw":
      context.user_data.clear()
      context.user_data["admin_action"] = "withdraw"
      await query.edit_message_text("أدخل معرف المستخدم والمبلغ للسحب (مثال: 123456789 5)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if data == "admin_add_seller_cb":
      context.user_data.clear()
      context.user_data["admin_action"] = "add_seller"
      await query.edit_message_text("أدخل معرف البائع والاسم (مثال: 123456789 @sellername)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if data == "admin_remove_seller_cb":
      context.user_data.clear()
      context.user_data["admin_action"] = "remove_seller"
      await query.edit_message_text("أدخل معرف البائع للحذف (مثال: 123456789)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if data == "admin_manage_files":
      DATAF = load_data()
      files = DATAF.get("files", {})
      if not files:
          await query.edit_message_text("No files uploaded." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      keyboard = []
      for prod in files.keys():
          keyboard.append([InlineKeyboardButton(prod, callback_data=f"admin_send_file:{prod}"), InlineKeyboardButton("Delete", callback_data=f"admin_delete_file:{prod}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Manage uploaded files:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_send_file:"):
      _, prod = data.split(":", 1)
      DATAF = load_data()
      file_ref = DATAF.get("files", {}).get(prod)
      if not file_ref:
          await query.edit_message_text("File not found." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
          return
      try:
          # if local path exists, send local file; else use stored file_id
          if os.path.exists(file_ref):
              await context.bot.send_document(chat_id=query.from_user.id, document=InputFile(file_ref))
          else:
              candidate = file_ref
              if not os.path.exists(candidate) and os.path.exists(os.path.join(os.getcwd(), candidate)):
                  candidate = os.path.join(os.getcwd(), candidate)
              if os.path.exists(candidate):
                  await context.bot.send_document(chat_id=query.from_user.id, document=InputFile(candidate))
              else:
                  # fallback: try sending as file_id
                  await context.bot.send_document(chat_id=query.from_user.id, document=file_ref)
          await query.edit_message_text(f"File {prod} sent to you." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
      except Exception as e:
          await query.edit_message_text("Failed to send file: " + str(e) + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
      return

  if data and data.startswith("admin_delete_file:"):
      _, prod = data.split(":", 1)
      DATAF = load_data()
      files = DATAF.get("files", {})
      if prod not in files:
          await query.edit_message_text("File not found." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
          return
      file_ref = files.get(prod)
      # attempt to remove local file if it exists and is within workspace
      try:
          if os.path.exists(file_ref):
              os.remove(file_ref)
      except Exception:
          pass
      # remove entries from data
      DATAF.get("files", {}).pop(prod, None)
      if "files_meta" in DATAF:
          DATAF.get("files_meta", {}).pop(prod, None)
      save_data(DATAF)
      await query.edit_message_text(f"Deleted file for product {prod}." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
      return

  # Seller requesting file via callback (if using inline flow)
  if data and data.startswith("seller_get_file:"):
      _, prod = data.split(":", 1)
      DATA = load_data()
      uid = str(query.from_user.id)
      if uid not in DATA.get("sellers", {}):
          await query.edit_message_text("Only sellers can download product files." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
          return
      files = DATA.get("files", {})
      file_ref = files.get(prod)
      if not file_ref:
          await query.edit_message_text("No file uploaded for this product." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
          return
      try:
          # If stored path exists locally, send local file, else fallback to telegram file_id
          if os.path.exists(file_ref):
              await context.bot.send_document(chat_id=query.from_user.id, document=InputFile(file_ref))
          else:
              candidate = file_ref
              if not os.path.exists(candidate) and os.path.exists(os.path.join(os.getcwd(), candidate)):
                  candidate = os.path.join(os.getcwd(), candidate)
              if os.path.exists(candidate):
                  await context.bot.send_document(chat_id=query.from_user.id, document=InputFile(candidate))
              else:
                  await context.bot.send_document(chat_id=query.from_user.id, document=file_ref)
          await query.edit_message_text("File sent." + SIGNATURE)
      except Exception as e:
          await query.edit_message_text("Failed to send file: " + str(e) + SIGNATURE)
      return


# ========== MESSAGE HANDLER ==========
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # Admin: Withdraw keys logic
  if context.user_data.get("admin_action") == "withdraw_keys":
      try:
          parts = text.split()
          product, duration, qty = parts[0], parts[1], int(parts[2])
          data = load_data()
          key_name = f"{product}_{duration}"
          keys_pool = data["keys"].get(key_name, [])
          used_keys = set(data.get("used_keys", []))
          available = [k for k in keys_pool if k not in used_keys]
          if len(available) < qty:
              await update.message.reply_text(f"❌ لا يوجد مفاتيح كافية للسحب. المتوفر: {len(available)}" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
              return
          withdrawn = available[:qty]
          # Mark as used (simulate withdrawal)
          data.setdefault("used_keys", [])
          data["used_keys"] = list(set(data.get("used_keys", [])).union(withdrawn))
          save_data(data)
          keys_str = "\n".join([f"`{k}`" for k in withdrawn])
          await update.message.reply_text(f"✅ تم سحب المفاتيح:\n{keys_str}" + SIGNATURE, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          context.user_data.pop("admin_action", None)
      except Exception as e:
          await update.message.reply_text("❌ صيغة خاطئة. مثال: FREE 7 2" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          context.user_data.pop("admin_action", None)
      return
  # record user as known
  try:
      DATA_LOCAL = load_data()
      uid = str(update.message.from_user.id)
      if uid not in DATA_LOCAL.get("users", []):
          DATA_LOCAL.setdefault("users", []).append(uid)
          save_data(DATA_LOCAL)
  except Exception:
      pass

  # handle text and documents
  text = update.message.text.strip() if update.message.text else ""

  # handle uploaded document for admin file upload
  if update.message.document and context.user_data.get("admin_action") == "upload_file":
      prod = context.user_data.get("upload_product")
      if not prod:
          await update.message.reply_text("No product selected for file upload." + SIGNATURE)
      else:
          DATA2 = load_data()
          try:
              # ensure files folder exists
              files_dir = os.path.join(os.getcwd(), "files")
              os.makedirs(files_dir, exist_ok=True)
              doc = update.message.document
              file_id = doc.file_id
              original_name = getattr(doc, "file_name", None) or f"{prod}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.dat"
              # sanitize filename
              safe_name = original_name.replace("/", "_").replace("\\", "_")
              local_path = os.path.join(files_dir, safe_name)
              # download file from Telegram to local path
              tg_file = await context.bot.get_file(file_id)
              await tg_file.download_to_drive(local_path)
              # store local relative path in DATA
              rel_path = os.path.relpath(local_path, os.getcwd())
              DATA2.setdefault("files", {})[prod] = rel_path
              # also keep telegram file_id as fallback
              DATA2.setdefault("files_meta", {})[prod] = {"tg_file_id": file_id, "local": rel_path}
              save_data(DATA2)
              await update.message.reply_text(f"File saved for product {prod} to {rel_path}." + SIGNATURE)
          except Exception as e:
              await update.message.reply_text("Failed to save file: " + str(e) + SIGNATURE)
      context.user_data.pop("admin_action", None)
      context.user_data.pop("upload_product", None)
      return

  PRICE_NEWLINE_TOKEN = "<br>"

  # Handle reply keyboard main options
  lang = context.user_data.get("lang", "en")
  # Button texts for all supported languages
  button_texts = {
      "buy": {"en": "🛍️ BUY KEYS", "ar": "🛍️ شراء مفاتيح", "fr": "🛍️ Acheter des clés", "es": "🛍️ Comprar claves", "de": "🛍️ Schlüssel kaufen", "tr": "🛍️ Anahtar Satın Al"},
      "balance": {"en": "💰 MY BALANCE", "ar": "💰 رصيدي", "fr": "💰 Mon solde", "es": "💰 Mi saldo", "de": "💰 Mein Guthaben", "tr": "💰 Bakiyem"},
      "admin": {"en": "🔐 ADMIN PANEL", "ar": "🔐 لوحة الادمن", "fr": "🔐 Panneau admin", "es": "🔐 Panel admin", "de": "🔐 Admin-Bereich", "tr": "🔐 Admin Paneli"},
      "lang": {"en": "🌐 Change Language", "ar": "🌐 تغيير اللغة", "fr": "🌐 Changer de langue", "es": "🌐 Cambiar idioma", "de": "🌐 Sprache ändern", "tr": "🌐 Dili Değiştir"},
      "activity": {"en": "📊 Activity", "ar": "📊 الاحصائيات", "fr": "📊 Activité", "es": "📊 Actividad", "de": "📊 Aktivität", "tr": "📊 Aktivite"}
  }
  if "get_files" not in button_texts:
      button_texts["get_files"] = {"en": "📁 Get Files", "ar": "📁 الحصول على الملفات"}

  # Back button in reply keyboard
  if text == "⬅️ Back":
      context.user_data.clear()
      await start(update, context)
      return

  # Activity (reply keyboard)
  if text == button_texts["activity"][lang]:
      DATA_STAT = load_data()
      uid = str(update.message.from_user.id)
      admins = set(DATA_STAT.get("admins", []))
      sellers_map = DATA_STAT.get("sellers", {})
      if uid not in admins and uid not in sellers_map:
          await update.message.reply_text("❌ Permission denied. Activity is for admins and sellers only." + SIGNATURE)
          return

      # Seller view
      if uid in sellers_map:
          seller = sellers_map.get(uid, {})
          balance = seller.get("balance", 0)
          sales = [s for s in DATA_STAT.get("sales_log", []) if s.get("seller_id") == uid]
          sold_count = len(sales)
          by_product = {}
          for s in sales:
              by_product[s.get("product")] = by_product.get(s.get("product"), 0) + 1
          msg = f"📊 Seller Activity ({seller.get('name','Unknown')} - {uid}):\n\nBalance: ${balance}\nKeys sold: {sold_count}\n\nSold by product:\n"
          if by_product:
              for p, c in by_product.items():
                  msg += f"- {p}: {c}\n"
          else:
              msg += "(no sales yet)\n"
          await update.message.reply_text(msg + SIGNATURE)
          return

      # Admin view
      start_clicks = DATA_STAT.get("start_clicks", 0)
      users_count = len(DATA_STAT.get("users", []))
      used_keys = DATA_STAT.get("used_keys", []) or []
      total_keys_sold = len(used_keys)
      total_keys_available = sum(len(v) for v in DATA_STAT.get("keys", {}).values())
      sellers = DATA_STAT.get("sellers", {})
      sellers_count = len(sellers)
      sales_count = len(DATA_STAT.get("sales_log", []))
      sold_by_product = {}
      for s in DATA_STAT.get("sales_log", []):
          sold_by_product[s.get("product")] = sold_by_product.get(s.get("product"), 0) + 1
      msg = f"📊 Bot Activity Summary:\n\nStart clicks: {start_clicks}\nKnown users: {users_count}\nTotal sales entries: {sales_count}\nKeys sold: {total_keys_sold}\nKeys available: {total_keys_available}\nSellers: {sellers_count}\n\nSold by product:\n"
      for prod, cnt in sold_by_product.items():
          msg += f"- {prod}: {cnt}\n"
      msg += "\nPer-seller breakdown:\n"
      if sellers:
          for sid, info in sellers.items():
              s_sales = [s for s in DATA_STAT.get("sales_log", []) if s.get("seller_id") == sid]
              s_count = len(s_sales)
              prod_counts = {}
              for s in s_sales:
                  prod_counts[s.get("product")] = prod_counts.get(s.get("product"), 0) + 1
              msg += f"- {info.get('name','?')} ({sid}) — Balance: ${info.get('balance',0)} — Keys sold: {s_count}\n"
              if prod_counts:
                  for p, c in prod_counts.items():
                      msg += f"    • {p}: {c}\n"
      else:
          msg += "(no sellers configured)\n"
      await update.message.reply_text(msg + SIGNATURE)
      return

  # Main menu: BUY
  if text == button_texts["buy"][lang]:
      PRICES = load_prices()
      products = list(PRICES["global"].keys())
      product_names = {
          "FREE": {"en": "🔮 FREE FIRE", "ar": "🔮 فري فاير", "fr": "🔮 FREE FIRE", "es": "🔮 FREE FIRE", "de": "🔮 FREE FIRE", "tr": "🔮 FREE FIRE"},
          "WIZARD": {"en": "✨ WIZARD", "ar": "✨ ويزارد", "fr": "✨ WIZARD", "es": "✨ WIZARD", "de": "✨ WIZARD", "tr": "✨ WIZARD"},
          "DRIP": {"en": "💧 DRIP", "ar": "💧 دريب", "fr": "💧 DRIP", "es": "💧 DRIP", "de": "💧 DRIP", "tr": "💧 DRIP"},
          "CERT": {"en": "🎖️ CERTIFICATE", "ar": "🎖️ شهادة", "fr": "🎖️ CERTIFICAT", "es": "🎖️ CERTIFICADO", "de": "🎖️ ZERTIFIKAT", "tr": "🎖️ SERTİFİKA"},
          "CLOUD": {"en": "☁️ CLOUD", "ar": "☁️ كلاود", "fr": "☁️ CLOUD", "es": "☁️ CLOUD", "de": "☁️ CLOUD", "tr": "☁️ CLOUD"},
          "CODM_IOS": {"en": "📱 CODM IOS", "ar": "📱 كودم IOS", "fr": "📱 CODM IOS", "es": "📱 CODM IOS", "de": "📱 CODM IOS", "tr": "📱 CODM IOS"},
          "TERMINAL_X_PC": {"en": "💻 TERMINAL X PC", "ar": "💻 تيرمنال X PC", "fr": "💻 TERMINAL X PC", "es": "💻 TERMINAL X PC", "de": "💻 TERMINAL X PC", "tr": "💻 TERMINAL X PC"},
          "HG_CHEATS_ROOT": {"en": "🛡️ HG CHEATS ROOT", "ar": "🛡️ HG شيتس روت", "fr": "🛡️ HG CHEATS ROOT", "es": "🛡️ HG CHEATS ROOT", "de": "🛡️ HG CHEATS ROOT", "tr": "🛡️ HG CHEATS ROOT"}
      }
      reply_keyboard = [[product_names[p][lang]] for p in products]
      reply_keyboard.append([button_texts["lang"][lang]])
      # if user is a seller, add Get Files button
      DATA_CHECK = load_data()
      uid = str(update.message.from_user.id)
      if uid in DATA_CHECK.get("sellers", {}):
          reply_keyboard.append([button_texts["get_files"][lang]])
      reply_keyboard.append(["⬅️ Back"])
      await update.message.reply_text(
          "Select a product:" if lang == "en" else
          "اختر المنتج:" if lang == "ar" else
          "Sélectionnez un produit:" if lang == "fr" else
          "Seleccione un producto:" if lang == "es" else
          "Produkt auswählen:" if lang == "de" else
          "Bir ürün seçin:",
          reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
      )
      context.user_data["buy_menu"] = True
      return

  # Main menu: BALANCE
  if text == button_texts["balance"][lang]:
      user_id = str(update.message.from_user.id)
      data = load_data()
      bal = data["balances"].get(user_id, 0)
      msg = {
          "en": f"Your balance: ${bal}",
          "ar": f"رصيدك: ${bal}",
          "fr": f"Votre solde: ${bal}",
          "es": f"Su saldo: ${bal}",
          "de": f"Ihr Guthaben: ${bal}",
          "tr": f"Bakiyeniz: ${bal}"
      }[lang]
      await update.message.reply_text(msg + SIGNATURE)
      return

  # Main menu: ADMIN (await code)
  if text == button_texts["admin"][lang]:
      msg = {
          "en": "Enter admin code:",
          "ar": "ادخل رمز الادمن:",
          "fr": "Entrez le code admin:",
          "es": "Ingrese el código de administrador:",
          "de": "Admin-Code eingeben:",
          "tr": "Yönetici kodunu girin:"
      }[lang]
      for k in ("buy_menu", "choose_duration", "choose_qty", "getting_file", "upload_product", "admin_action"):
          context.user_data.pop(k, None)
      await update.message.reply_text(msg + SIGNATURE)
      context.user_data["awaiting_admin_code"] = True
      return

  # Language selection via reply keyboard
  if text == button_texts["lang"][lang]:
      LANGUAGES = {
          "en": "English",
          "ar": "العربية",
          "fr": "Français",
          "es": "Español",
          "de": "Deutsch",
          "tr": "Türkçe"
      }
      lang_keyboard = [[InlineKeyboardButton(LANGUAGES[code], callback_data=f"set_lang:{code}")] for code in LANGUAGES]
      await update.message.reply_text(
          "Please select your language:\nيرجى اختيار اللغة:" + SIGNATURE,
          reply_markup=InlineKeyboardMarkup(lang_keyboard)
      )
      return

  # Seller: request files via reply keyboard
  if text == button_texts["get_files"][lang]:
      DATAF = load_data()
      files = DATAF.get("files", {})
      uid = str(update.message.from_user.id)
      # If user is a seller, show all files; otherwise show only purchased products
      if uid in DATAF.get("sellers", {}):
          available = list(files.keys())
      else:
          purchases = [s.get("product") for s in DATAF.get("sales_log", []) if s.get("user") == uid]
          available = sorted(set(purchases))
      if not available:
          await update.message.reply_text("No files available for you." + SIGNATURE)
          return
      product_names = {k: {"en": k, "ar": k} for k in available}
      reply_keyboard = [[product_names[p][lang]] for p in available]
      reply_keyboard.append(["⬅️ Back"])
      await update.message.reply_text("Select product to download file:" + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      context.user_data["getting_file"] = True
      return

  # If seller selects a product name to get file
  if context.user_data.get("getting_file"):
      DATAF = load_data()
      sel = None
      for p in DATAF.get("files", {}).keys():
          if text == p or p.lower() in text.lower() or p in text:
              sel = p
              break
      if sel:
          file_ref = DATAF.get("files", {}).get(sel)
          if file_ref:
              try:
                  # check permission: seller or purchaser
                  uid = str(update.message.from_user.id)
                  allowed = False
                  if uid in DATAF.get("sellers", {}):
                      allowed = True
                  else:
                      # check sales_log for purchases
                      for s in DATAF.get("sales_log", []):
                          if s.get("user") == uid and s.get("product") == sel:
                              allowed = True
                              break
                  if not allowed:
                      await update.message.reply_text("You don't have access to this file." + SIGNATURE)
                      context.user_data.pop("getting_file", None)
                      return
                  if os.path.exists(file_ref):
                      await update.message.reply_document(document=InputFile(file_ref))
                  else:
                      candidate = file_ref
                      if not os.path.exists(candidate) and os.path.exists(os.path.join(os.getcwd(), candidate)):
                          candidate = os.path.join(os.getcwd(), candidate)
                      if os.path.exists(candidate):
                          await update.message.reply_document(document=InputFile(candidate))
                      else:
                          await update.message.reply_document(document=file_ref)
                  context.user_data.pop("getting_file", None)
                  return
              except Exception as e:
                  await update.message.reply_text("Failed to send file: " + str(e) + SIGNATURE)
                  context.user_data.pop("getting_file", None)
                  return

  # If user is in buy menu and selects a product, show durations
  if context.user_data.get("buy_menu"):
      PRICES = load_prices()
      product_names = {
          "FREE": {"en": "🔮 FREE FIRE", "ar": "🔮 فري فاير", "fr": "🔮 FREE FIRE", "es": "🔮 FREE FIRE", "de": "🔮 FREE FIRE", "tr": "🔮 FREE FIRE"},
          "WIZARD": {"en": "WIZARD", "ar": "ويزارد", "fr": "WIZARD", "es": "WIZARD", "de": "WIZARD", "tr": "WIZARD"},
          "DRIP": {"en": "DRIP", "ar": "دريب", "fr": "DRIP", "es": "DRIP", "de": "DRIP", "tr": "DRIP"},
          "CERT": {"en": "CERTIFICATE", "ar": "شهادة", "fr": "CERTIFICAT", "es": "CERTIFICADO", "de": "ZERTIFIKAT", "tr": "SERTİFİKA"},
          "CLOUD": {"en": "CLOUD", "ar": "كلاود", "fr": "CLOUD", "es": "CLOUD", "de": "CLOUD", "tr": "CLOUD"},
          "CODM_IOS": {"en": "CODM IOS", "ar": "كودم IOS", "fr": "CODM IOS", "es": "CODM IOS", "de": "CODM IOS", "tr": "CODM IOS"},
          "TERMINAL_X_PC": {"en": "TERMINAL X PC", "ar": "تيرمنال X PC", "fr": "TERMINAL X PC", "es": "TERMINAL X PC", "de": "TERMINAL X PC", "tr": "TERMINAL X PC"},
          "HG_CHEATS_ROOT": {"en": "HG CHEATS ROOT", "ar": "HG شيتس روت", "fr": "HG CHEATS ROOT", "es": "HG CHEATS ROOT", "de": "HG CHEATS ROOT", "tr": "HG CHEATS ROOT"}
      }
      selected_product = None
      lower_text = text.lower()
      for key, names in product_names.items():
          display = names[lang]
          if text == display or display in text or key.lower() in lower_text or key in text:
              selected_product = key
              break
      if selected_product:
          durations = list(PRICES.get("global", {}).get(selected_product, {}).keys())
          if not durations:
              await update.message.reply_text(f"⚠️ No pricing/config found for {selected_product}. Ask the admin to set prices or add keys." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buy_menu")]]))
              return
          duration_names = {
              "1": {"en": "1 day", "ar": "يوم", "fr": "1 jour", "es": "1 día", "de": "1 Tag", "tr": "1 gün"},
              "7": {"en": "7 days", "ar": "7 أيام", "fr": "7 jours", "es": "7 días", "de": "7 Tage", "tr": "7 gün"},
              "15": {"en": "15 days", "ar": "15 يوم", "fr": "15 jours", "es": "15 días", "de": "15 Tage", "tr": "15 gün"},
              "31": {"en": "1 month", "ar": "شهر", "fr": "1 mois", "es": "1 mes", "de": "1 Monat", "tr": "1 ay"},
              "365": {"en": "1 year", "ar": "سنة", "fr": "1 an", "es": "1 año", "de": "1 Jahr", "tr": "1 yıl"}
          }
          reply_keyboard = [[duration_names[d][lang]] for d in durations if d in duration_names]
          reply_keyboard.append([button_texts["lang"][lang]])
          reply_keyboard.append(["⬅️ Back"])
          await update.message.reply_text(
              "Select duration:" if lang == "en" else
              "اختر المدة:" if lang == "ar" else
              "Sélectionnez la durée:" if lang == "fr" else
              "Seleccione la duración:" if lang == "es" else
              "Dauer auswählen:" if lang == "de" else
              "Süre seçin:",
              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
          )
          context.user_data["selected_product"] = selected_product
          context.user_data["buy_menu"] = False
          context.user_data["choose_duration"] = True
          return

  # If user is in choose_duration and selects a duration, show quantity (1-10)
  if context.user_data.get("choose_duration"):
      selected_product = context.user_data.get("selected_product")
      PRICES = load_prices()
      durations = list(PRICES["global"][selected_product].keys())
      duration_names = {
          "1": {"en": "1 day", "ar": "يوم", "fr": "1 jour", "es": "1 día", "de": "1 Tag", "tr": "1 gün"},
          "7": {"en": "7 days", "ar": "7 أيام", "fr": "7 jours", "es": "7 días", "de": "7 Tage", "tr": "7 gün"},
          "15": {"en": "15 days", "ar": "15 يوم", "fr": "15 jours", "es": "15 días", "de": "15 Tage", "tr": "15 gün"},
          "31": {"en": "1 month", "ar": "شهر", "fr": "1 mois", "es": "1 mes", "de": "1 Monat", "tr": "1 ay"},
          "365": {"en": "1 year", "ar": "سنة", "fr": "1 an", "es": "1 año", "de": "1 Jahr", "tr": "1 yıl"}
      }
      selected_duration = None
      for d in durations:
          if text == duration_names[d][lang]:
              selected_duration = d
              break
      if selected_duration:
          reply_keyboard = [[str(i)] for i in range(1, 11)]
          reply_keyboard.append([button_texts["lang"][lang]])
          reply_keyboard.append(["⬅️ Back"])
          await update.message.reply_text(
              "Select quantity:" if lang == "en" else
              "اختر الكمية:" if lang == "ar" else
              "Sélectionnez la quantité:" if lang == "fr" else
              "Seleccione la cantidad:" if lang == "es" else
              "Menge auswählen:" if lang == "de" else
              "Adet seçin:",
              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
          )
          context.user_data["selected_duration"] = selected_duration
          context.user_data["choose_duration"] = False
          context.user_data["choose_qty"] = True
          return

  # If user is in choose_qty and selects a quantity, process purchase
  if context.user_data.get("choose_qty"):
      try:
          qty = int(text)
          if not (1 <= qty <= 10):
              raise ValueError()
      except:
          await update.message.reply_text("Invalid quantity!" if lang == "en" else "كمية غير صالحة!" if lang == "ar" else "Quantité invalide!" if lang == "fr" else "¡Cantidad inválida!" if lang == "es" else "Ungültige Menge!" if lang == "de" else "Geçersiz miktar!", reply_markup=None)
          return
      selected_product = context.user_data.get("selected_product")
      selected_duration = context.user_data.get("selected_duration")
      PRICES = load_prices()
      DATA = load_data()
      price = PRICES["global"][selected_product][selected_duration] * qty
      user_id = str(update.message.from_user.id)
      try:
          balance = float(DATA["balances"].get(user_id, 0))
      except:
          balance = 0
      key_name = f"{selected_product}_{selected_duration}"
      keys_pool = DATA["keys"].get(key_name, [])
      used_keys = set(DATA.get("used_keys", []))
      keys_pool = [k for k in keys_pool if k not in used_keys]
      if balance < price:
          await update.message.reply_text(("❌ Insufficient balance!\nPrice: $" + str(price) + "\nYour balance: $" + str(balance)) if lang == "en" else "❌ الرصيد غير كاف!\nالسعر: $" + str(price) + "\nرصيدك: $" + str(balance) if lang == "ar" else "❌ Solde insuffisant!\nPrix: $" + str(price) + "\nVotre solde: $" + str(balance) if lang == "fr" else "❌ ¡Saldo insuficiente!\nPrecio: $" + str(price) + "\nSu saldo: $" + str(balance) if lang == "es" else "❌ Unzureichendes Guthaben!\nPreis: $" + str(price) + "\nIhr Guthaben: $" + str(balance) if lang == "de" else "❌ Yetersiz bakiye!\nFiyat: $" + str(price) + "\nBakiyeniz: $" + str(balance), reply_markup=None)
          return
      if len(keys_pool) < qty:
          if lang == "en":
              msg = f"❌ Not enough keys available for {selected_product} - {selected_duration} days, quantity {qty}."
          elif lang == "ar":
              msg = f"❌ لا يوجد مفاتيح كافية لـ {selected_product} - {selected_duration} يوم، الكمية {qty}."
          elif lang == "fr":
              msg = f"❌ Pas assez de clés disponibles pour {selected_product} - {selected_duration} jours, quantité {qty}."
          elif lang == "es":
              msg = f"❌ No hay suficientes claves disponibles para {selected_product} - {selected_duration} días, cantidad {qty}."
          elif lang == "de":
              msg = f"❌ Nicht genügend Schlüssel verfügbar für {selected_product} - {selected_duration} Tage, Menge {qty}."
          else:
              msg = f"❌ Yeterli anahtar yok: {selected_product} - {selected_duration} gün, miktar {qty}."
          await update.message.reply_text(msg, reply_markup=None)
          return
      keys = [keys_pool.pop(0) for _ in range(qty)]
      DATA["used_keys"] = list(set(DATA.get("used_keys", [])).union(keys))
      DATA["keys"][key_name] = keys_pool
      DATA["balances"][user_id] = balance - price
      for k in keys:
          sale_entry = {"user": user_id, "product": selected_product, "duration": selected_duration, "price": PRICES["global"][selected_product][selected_duration], "buyer_balance": balance - price}
          DATA["sales_log"].append(sale_entry)
      # Notify all admins about the purchase
      admins = DATA.get("admins", [])
      buyer_balance = balance - price
      product_name = selected_product
      duration = selected_duration
      for admin_id in admins:
          try:
              await context.bot.send_message(
                  chat_id=int(admin_id),
                  text=f"🔔 تم شراء مفاتيح\nالمنتج: {product_name}\nالمدة: {duration} يوم\nرصيد المشتري بعد الشراء: ${buyer_balance}"
              )
          except Exception:
              pass
      save_data(DATA)
      keys_str = "\n".join([f"`{k}`" for k in keys])
      await update.message.reply_text((f"✅ Purchase successful!\n\nYour keys:\n{keys_str}") if lang == "en" else f"✅ تم الشراء بنجاح!\n\nمفاتيحك:\n{keys_str}" if lang == "ar" else f"✅ Achat réussi!\n\nVos clés:\n{keys_str}" if lang == "fr" else f"✅ ¡Compra exitosa!\n\nSus claves:\n{keys_str}" if lang == "es" else f"✅ Kauf erfolgreich!\n\nIhre Schlüssel:\n{keys_str}" if lang == "de" else f"✅ Satın alma başarılı!\n\nAnahtarlarınız:\n{keys_str}", parse_mode="Markdown")
      context.user_data.pop("selected_product", None)
      context.user_data.pop("selected_duration", None)
      context.user_data.pop("choose_qty", None)
      return

  if context.user_data.get("awaiting_admin_code"):
      if text == ADMIN_CODE:
          context.user_data.pop("awaiting_admin_code", None)
          # persist this user as an admin
          try:
              DATA_AD = load_data()
              uid = str(update.message.from_user.id)
              DATA_AD.setdefault("admins", [])
              if uid not in DATA_AD["admins"]:
                  DATA_AD["admins"].append(uid)
                  save_data(DATA_AD)
          except Exception:
              pass
          context.user_data["is_admin"] = True
          await update.message.reply_text("👍 Admin panel access granted." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([
              [InlineKeyboardButton("Main Menu", callback_data="admin_menu")]]))
      else:
          await update.message.reply_text("❌ Wrong code!" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([
                  [InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]
              ]))
      return

  action = context.user_data.get("admin_action")
  # Handle broadcast, seller balance add from admin callback and other admin actions
  if action == "broadcast":
      text_to_send = text
      data = load_data()
      users = data.get("users", [])
      sent = 0
      failed = 0
      for u in users:
          try:
              await context.bot.send_message(chat_id=int(u), text=text_to_send + SIGNATURE)
              sent += 1
          except Exception:
              failed += 1
      await update.message.reply_text(f"Broadcast complete. Sent: {sent}, Failed: {failed}" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      context.user_data.pop("admin_action", None)
      return
  if action == "add_balance":
      try:
          parts = text.split()
          uid, amount = parts[0], float(parts[1])
          data = load_data()
          data["balances"][uid] = data["balances"].get(uid, 0) + amount
          save_data(data)
          await update.message.reply_text(f"✅ Added ${amount} to user {uid}. Balance: ${data['balances'][uid]}" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          context.user_data.pop("admin_action", None)
      except:
          await update.message.reply_text("❌ Wrong format: user_id amount" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if action == "withdraw":
      try:
          parts = text.split()
          uid, amount = parts[0], float(parts[1])
          data = load_data()
          if data["balances"].get(uid, 0) < amount:
              await update.message.reply_text(f"❌ Insufficient balance! Available: ${data['balances'].get(uid, 0)}" + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          else:
              data["balances"][uid] -= amount
              save_data(data)
              await update.message.reply_text(f"✅ Withdrawn ${amount} from {uid}. Balance: ${data['balances'][uid]}" + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
              context.user_data.pop("admin_action", None)
      except:
          await update.message.reply_text("❌ Wrong format: user_id amount" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if action == "add_keys":
      product = context.user_data.get("add_keys_product")
      duration = context.user_data.get("add_keys_duration")
      if not product or not duration:
          await update.message.reply_text("❌ يجب اختيار المنتج والمدة أولاً من لوحة الأدمن." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")]]))
          return
      keys = [k.strip() for k in text.split("\n") if k.strip()]
      if not keys:
          await update.message.reply_text("❌ لم يتم إدخال أي مفاتيح. أرسل المفاتيح (كل مفتاح في سطر)." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=f"admin_add_keys_duration:{product}:{duration}")]]))
          return
      
      # Add keys to database
      add_keys_to_db(product, duration, keys)
      
      # Also update local data
      data = load_data()
      key_name = f"{product}_{duration}"
      if key_name not in data["keys"]:
          data["keys"][key_name] = []
      data["keys"][key_name].extend(keys)
      save_data(data)
      
      await update.message.reply_text(f"✅ تم إضافة {len(keys)} مفتاح لـ {product} ({duration}يوم)." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=f"admin_add_keys_product:{product}")]]))
      context.user_data.clear()
      return
  if action == "add_seller_balance":
      try:
          sid = context.user_data.get("target_seller")
          amount = float(text)
          data = load_data()
          if sid not in data.get("sellers", {}):
              await update.message.reply_text("❌ Seller not found!" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
          else:
              data["sellers"][sid]["balance"] = data["sellers"][sid].get("balance", 0) + amount
              save_data(data)
              await update.message.reply_text(f"✅ Added ${amount} to seller {sid}. New balance: ${data['sellers'][sid]['balance']}" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      except Exception:
          await update.message.reply_text("❌ Wrong format: amount" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      context.user_data.pop("admin_action", None)
      context.user_data.pop("target_seller", None)
      return
  if action == "admin_set_seller_price":
      seller_id = context.user_data.get("seller_id")
      product = context.user_data.get("product")
      duration = str(context.user_data.get("duration"))  # تحويل إلى string
      try:
          price_val = float(text)
          prices = load_prices()
          if seller_id not in prices.get("sellers", {}):
              prices.setdefault("sellers", {})[seller_id] = {}
          if product not in prices["sellers"][seller_id]:
              prices["sellers"][seller_id][product] = {}
          prices["sellers"][seller_id][product][duration] = price_val
          save_prices(prices)
          await update.message.reply_text(
              f"✅ تم تعديل سعر البائع!\n\nالبائع: {seller_id}\nالمنتج: {product}\nالمدة: {duration} يوم\nالسعر الجديد: ${price_val}" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=f"admin_select_seller_price:{seller_id}")]]))
      except Exception as e:
          await update.message.reply_text("❌ أدخل رقم صحيح للسعر." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=f"admin_seller_edit_price:{seller_id}:{product}:{duration}")]]))
      context.user_data.pop("admin_action", None)
      context.user_data.pop("seller_id", None)
      context.user_data.pop("product", None)
      context.user_data.pop("duration", None)
      return
  if action == "create_key":
      product = context.user_data.get("create_key_product")
      duration = context.user_data.get("create_key_duration")
      key = text.strip()
      data = load_data()
      key_name = key_storage_name(product, duration)
      if key_name not in data["keys"]:
          data["keys"][key_name] = []
      data["keys"][key_name].append(key)
      save_data(data)
      await update.message.reply_text(
          f"✅ تم إنشاء الكيز لـ {product} ({duration}يوم)!\n\nها هو الكيز:\n`{key}`" + SIGNATURE, parse_mode="Markdown",
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="admin_create_key_product:"+product)]]))
      context.user_data.pop("admin_action", None)
      context.user_data.pop("create_key_product", None)
      context.user_data.pop("create_key_duration", None)
      return
  if action == "set_price":
      product = context.user_data.get("edit_price_product")
      duration = context.user_data.get("edit_price_days")
      seller_id = context.user_data.get("edit_price_seller")
      try:
          price_val = float(text)
          prices = load_prices()
          if seller_id not in prices["sellers"]:
              prices["sellers"][seller_id] = {}
          if product not in prices["sellers"][seller_id]:
              prices["sellers"][seller_id][product] = {}
          prices["sellers"][seller_id][product][duration] = price_val
          save_prices(prices)
          await update.message.reply_text(
              f"✅ تم تعديل السعر: {product} ({duration}يوم) - السعر الجديد للبائع {seller_id}: ${price_val}" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=f"edit_price:{product}")]]))
      except Exception as e:
          await update.message.reply_text("❌ أدخل رقم صحيح للسعر." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=f"edit_price:{product}")]]))
      context.user_data.pop("admin_action", None)
      context.user_data.pop("edit_price_product", None)
      context.user_data.pop("edit_price_days", None)
      return
  if action == "add_seller":
      try:
          parts = text.split(maxsplit=1)
          sid, name = parts[0], parts[1] if len(parts) > 1 else "Unknown"
          data = load_data()
          data["sellers"][sid] = {"name": name, "balance": 0, "sales_count": 0}
          save_data(data)
          await update.message.reply_text(f"✅ Seller '{name}' (ID: {sid}) added." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
          context.user_data.pop("admin_action", None)
      except:
          await update.message.reply_text("❌ Wrong format: seller_id name" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      return
  if action == "remove_seller":
      data = load_data()
      sid = text.strip()
      if sid in data["sellers"]:
          name = data["sellers"][sid]["name"]
          del data["sellers"][sid]
          save_data(data)
          await update.message.reply_text(f"✅ Seller '{name}' (ID: {sid}) removed." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
          context.user_data.pop("admin_action", None)
      else:
          await update.message.reply_text("❌ Seller not found!" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      return
  if action == "seller_balance":
      try:
          parts = text.split()
          sid, amount = parts[0], float(parts[1])
          data = load_data()
          if sid not in data["sellers"]:
              await update.message.reply_text(f"❌ Seller {sid} not found!" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
          else:
              data["sellers"][sid]["balance"] = data["sellers"][sid].get("balance", 0) + amount
              save_data(data)
              name = data["sellers"][sid]["name"]
              await update.message.reply_text(f"✅ Added ${amount} to seller {name}. Balance: ${data['sellers'][sid]['balance']}" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
              context.user_data.pop("admin_action", None)
      except:
          await update.message.reply_text("❌ Wrong format: seller_id amount" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      return

# ========== MAIN ==========
def main():
 if not TOKEN:
     print("❌ Error: TELEGRAM_BOT_TOKEN not set!")
     print("📝 Set it as an environment variable on Render:")
     print("   1. Go to Dashboard → Your Service")
     print("   2. Click Environment")
     print("   3. Add: TELEGRAM_BOT_TOKEN = 8216359066:AAG5awNOda7BbYaT_fclc-tZBvNTWuqht98")
     print("   4. Click Save")
     print("   5. Go back and click 'Redeploy' or restart the service")
     return
 
 print("✅ Token found!")
 # Initialize database
 init_db()
 
 app = Application.builder().token(TOKEN).build()
 app.add_handler(CommandHandler("start", start))
 app.add_handler(CallbackQueryHandler(callback_handler))
 app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
 print("Bot running...")
 try:
     # drop_pending_updates can help in some cases where old updates block flow
     app.run_polling(drop_pending_updates=True)
 except telegram.error.Conflict as e:
     print("Failed to start bot: another getUpdates poller is active for this token.")
     print("telegram.error.Conflict:", e)
     print("Make sure no other bot instance is running (other machines, containers, or processes).")
     print("On Windows you can list Python processes in PowerShell: Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' } | Select-Object ProcessId, CommandLine")
     return
 except Exception as e:
     print("Failed to start bot:", e)
     return

if __name__ == "__main__":
 main()
 
