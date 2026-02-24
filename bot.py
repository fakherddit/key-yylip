from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InputFile
import telegram
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
try:
  import requests
except Exception:
  requests = None
try:
  import psycopg as pg
except Exception:
  try:
      import psycopg2 as pg
  except Exception:
      pg = None

TOKEN = "7953606786:AAEborWiaCRvihbnL74Kw8S-WQfuimus4Wo"  # PUT YOUR BOT TOKEN HERE!
ADMIN_CODE = "123123NNK"
SIGNATURE = "\n\n© @FAKHERDDIN5"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "bot_data.json")
DB_FILE = os.path.join(DATA_DIR, "bot_data.sqlite3")
PRICES_FILE = os.path.join(BASE_DIR, "prices.json")
SELLER_CHANNEL_URL = "https://t.me/stonexff"
DEFAULT_LANG = "en"
PG_DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("POSTGRES_DSN")
    or "postgres://koyeb-adm:npg_VpavJAnOt1h5@ep-broad-shape-agttzbkf.c-2.eu-central-1.pg.koyeb.app/koyebdb"
)
FIRSTONE_BOT_TOKEN = os.getenv("FIRSTONE_BOT_TOKEN", "")


def _get_db_connection():
  conn = sqlite3.connect(DB_FILE)
  conn.execute("PRAGMA journal_mode=WAL;")
  conn.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
  return conn


def _get_pg_connection():
  if not PG_DATABASE_URL or not pg:
      return None
  conn = pg.connect(PG_DATABASE_URL)
  with conn.cursor() as cur:
      cur.execute("CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
  conn.commit()
  return conn


def _load_data_from_sqlite():
  try:
      conn = _get_db_connection()
      cur = conn.execute("SELECT value FROM kv WHERE key='data'")
      row = cur.fetchone()
      conn.close()
      if row and row[0]:
          return json.loads(row[0])
  except Exception:
      return None
  return None


def _load_data_from_postgres():
  try:
      conn = _get_pg_connection()
      if not conn:
          return None
      with conn.cursor() as cur:
          cur.execute("SELECT value FROM kv WHERE key='data'")
          row = cur.fetchone()
      conn.close()
      if row and row[0]:
          return json.loads(row[0])
  except Exception:
      return None
  return None


def _save_data_to_sqlite(data):
  try:
      payload = json.dumps(data, ensure_ascii=False)
      conn = _get_db_connection()
      conn.execute("INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", ("data", payload))
      conn.commit()
      conn.close()
      return True
  except Exception:
      return False


def _save_data_to_postgres(data):
  try:
      conn = _get_pg_connection()
      if not conn:
          return False
      payload = json.dumps(data, ensure_ascii=False)
      with conn.cursor() as cur:
          cur.execute("INSERT INTO kv (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value", ("data", payload))
      conn.commit()
      conn.close()
      return True
  except Exception:
      return False


def _load_data_from_storage():
  if PG_DATABASE_URL and pg:
      data = _load_data_from_postgres()
      if isinstance(data, dict):
          return data
  return _load_data_from_sqlite()


def _save_data_to_storage(data):
  if PG_DATABASE_URL and pg:
      return _save_data_to_postgres(data)
  return _save_data_to_sqlite(data)


def load_data():
  db_data = _load_data_from_storage()
  if isinstance(db_data, dict):
      return db_data
  try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
          data = json.load(f)
          _save_data_to_storage(data)
          return data
  except json.JSONDecodeError:
      try:
          corrupt_path = DATA_FILE + ".corrupt." + datetime.utcnow().strftime("%Y%m%d%H%M%S")
          os.replace(DATA_FILE, corrupt_path)
      except Exception:
          pass
  except Exception:
      pass
  default_data = {
      "balances": {},
      "sellers": {},
      "keys": {},
      "users": [],
      "files": {},
      "sales_log": [],
      "start_clicks": 0,
      "used_keys": [],
      "sold_keys": {},
      "seller_custom_buttons": [],
      "approved_users": [],
      "pending_users": [],
      "pending_payments": {},
      "admins": ["7210704553"],
  }
  _save_data_to_storage(default_data)
  return default_data


def save_data(data):
  _save_data_to_storage(data)
  tmp_path = DATA_FILE + ".tmp"
  with open(tmp_path, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2, ensure_ascii=False)
  os.replace(tmp_path, DATA_FILE)


def load_prices():
  defaults = {
      "global": {
          "FREE": {"1": 3, "7": 7, "31": 13},
          "WIZARD": {"1": 3, "7": 7, "31": 13},
          "DRIP": {"1": 1, "7": 2, "15": 4, "31": 6},
          "CERT_JIT_30": {"30": 3},
          "FF_IOS_FLUORIT": {"1": 2, "7": 8, "31": 16},
          "FF_IOS_MUGIL_PRO": {"31": 10.5},
          "HG_CHEAT_ANDROID": {"1": 2, "10": 3, "30": 6},
          "DRIP_CLIENT_ROOT_DEVICE": {"1": 1, "7": 3, "30": 6},
          "PATO_TEAM": {"3": 1, "7": 1.5, "15": 2.5, "30": 5}
      },
      "sellers": {}
  }
  try:
      with open(PRICES_FILE, "r", encoding="utf-8") as f:
          prices = json.load(f)
  except json.JSONDecodeError:
      try:
          corrupt_path = PRICES_FILE + ".corrupt." + datetime.utcnow().strftime("%Y%m%d%H%M%S")
          os.replace(PRICES_FILE, corrupt_path)
      except Exception:
          pass
      save_prices(defaults)
      return defaults
  except Exception:
      save_prices(defaults)
      return defaults

  if "global" not in prices:
      prices["global"] = {}
  if "sellers" not in prices:
      prices["sellers"] = {}

  changed = False
  for prod, durs in defaults["global"].items():
      if prod not in prices["global"]:
          prices["global"][prod] = durs
          changed = True
      else:
          for dur, val in durs.items():
              if str(dur) not in prices["global"][prod]:
                  prices["global"][prod][str(dur)] = val
                  changed = True

  desired_cert_prices = {
      "CERT_0": {"0": 3},
      "CERT_30": {"30": 4},
      "CERT_90": {"90": 5},
      "CERT_180": {"180": 8},
      "CERT_300": {"300": 10},
      "CERT_300_IPAD": {"300": 4},
      "CERT_JIT_0": {"0": 3},
      "CERT_JIT_30": {"30": 4}
  }
  for prod, durs in desired_cert_prices.items():
      prices.setdefault("global", {}).setdefault(prod, {})
      for dur, val in durs.items():
          if str(prices["global"][prod].get(str(dur))) != str(val):
              prices["global"][prod][str(dur)] = val
              changed = True

  # Ensure unwanted certs are removed and prices are updated
  keys_to_remove = ["CERT_0", "CERT_30", "CERT_90", "CERT_180", "CERT_300", "CERT_300_IPAD", "CERT_JIT_0"]
  for k in keys_to_remove:
      if k in prices.get("global", {}):
          del prices["global"][k]
          changed = True

  # Update Fluorit prices if they don't match
  fluorit_target = {"1": 2, "7": 8, "31": 16}
  current_fluorit = prices.get("global", {}).get("FF_IOS_FLUORIT", {})
  for dur, val in fluorit_target.items():
      if str(current_fluorit.get(str(dur))) != str(val):
          prices["global"].setdefault("FF_IOS_FLUORIT", {})[str(dur)] = val
          changed = True

  # Update Cert 30 price
  if prices.get("global", {}).get("CERT_JIT_30", {}).get("30") != 3:
      prices["global"].setdefault("CERT_JIT_30", {})["30"] = 3
      changed = True

  if "CERT" in prices.get("global", {}):
      prices["global"].pop("CERT", None)
      changed = True
  if "CERT_NORMAL" in prices.get("global", {}):
      prices["global"].pop("CERT_NORMAL", None)
      changed = True
  if "CERT_SUPER" in prices.get("global", {}):
      prices["global"].pop("CERT_SUPER", None)
      changed = True

  if changed:
      save_prices(prices)
  return prices


def save_prices(prices):
  tmp_path = PRICES_FILE + ".tmp"
  with open(tmp_path, "w", encoding="utf-8") as f:
      json.dump(prices, f, indent=2, ensure_ascii=False)
  os.replace(tmp_path, PRICES_FILE)


def get_price_for_user(prices, product, duration, user_id, data):
  """Get price for a user, checking seller-specific prices first"""
  # Check if user is a seller and has custom pricing
  if user_id in data.get("sellers", {}):
      seller_prices = prices.get("sellers", {}).get(user_id, {})
      if product in seller_prices and str(duration) in seller_prices[product]:
          return seller_prices[product][str(duration)]
  # Fallback to global pricing
  return prices.get("global", {}).get(product, {}).get(str(duration))


def key_storage_name(prod, dur):
  return f"{prod}_{dur}"


def build_rows(items, row_size=2):
  rows = []
  for i in range(0, len(items), row_size):
      rows.append(items[i:i + row_size])
  return rows


def build_seller_options_keyboard(data):
  rows = []
  for btn in data.get("seller_custom_buttons", []):
      label = btn.get("label") if isinstance(btn, dict) else None
      if label:
          rows.append([label])
  return rows


def send_cert_keys_via_firstone(user_id: str, keys: list, signature: str):
  if not FIRSTONE_BOT_TOKEN:
      return False, "FIRSTONE_BOT_TOKEN is not set"
  try:
      bot = telegram.Bot(token=FIRSTONE_BOT_TOKEN)
      keys_str = "\n".join([f"`{k}`" for k in keys])
      text = f"✅ Purchase successful!\n\nYour keys:\n{keys_str}" + signature
      bot.send_message(chat_id=int(user_id), text=text, parse_mode="Markdown")
      return True, None
  except Exception as e:
      return False, str(e)


def build_customer_activity_message(data: dict, uid: str):
  balance = data.get("balances", {}).get(uid, 0)
  purchases = [s for s in data.get("sales_log", []) if s.get("user") == uid]
  total = len(purchases)
  by_product = {}
  for s in purchases:
      prod = s.get("product")
      if prod:
          by_product[prod] = by_product.get(prod, 0) + 1
  msg = f"📊 Your Activity:\n\nBalance: ${balance}\nPurchases: {total}\n\nPurchases by product:\n"
  if by_product:
      for p, c in by_product.items():
          msg += f"- {p}: {c}\n"
  else:
      msg += "(no purchases yet)\n"
  return msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  lang = context.user_data.get("lang")
  if not lang:
      lang = DEFAULT_LANG
      context.user_data["lang"] = lang
  button_texts = {
      "buy": {"en": "🛍️ BUY KEYS", "ar": "🛍️ شراء مفاتيح"},
      "balance": {"en": "💰 MY BALANCE", "ar": "💰 رصيدي"},
      "admin": {"en": "🔐 ADMIN PANEL", "ar": "🔐 لوحة الادمن"},
      "about": {"en": "ℹ️ ABOUT", "ar": "ℹ️ حول"},
      "lang": {"en": "🌐 Change Language", "ar": "🌐 تغيير اللغة"},
      "activity": {"en": "📊 Activity", "ar": "📊 النشاط"},
      "get_files": {"en": "📁 Get Files", "ar": "📁 الحصول على الملفات"}
  }
  uid = None
  try:
      if getattr(update, "message", None):
          uid = str(update.message.from_user.id)
      elif getattr(update, "callback_query", None):
          uid = str(update.callback_query.from_user.id)
  except Exception:
      uid = None

  DATA_START = load_data()
  admins = set(DATA_START.get("admins", []))
  approved = set(DATA_START.get("approved_users", []))
  if uid and uid in DATA_START.get("sellers", {}):
      approved.add(uid)
      DATA_START.setdefault("approved_users", [])
      if uid not in DATA_START["approved_users"]:
          DATA_START["approved_users"].append(uid)

  if uid and uid not in admins and uid not in approved:
      DATA_START.setdefault("pending_users", [])
      if uid not in DATA_START["pending_users"]:
          DATA_START["pending_users"].append(uid)
      save_data(DATA_START)
      try:
          for admin_id in admins:
              await context.bot.send_message(
                  chat_id=int(admin_id),
                  text=f"طلب وصول جديد من المستخدم: {uid}",
                  reply_markup=InlineKeyboardMarkup([
                      [InlineKeyboardButton("✅ Accept", callback_data=f"admin_approve_user:{uid}")]
                  ])
              )
      except Exception:
          pass
      pending_text = "⏳ Your access request is pending admin approval." if lang == "en" else "⏳ طلبك قيد المراجعة من الأدمن."
      if getattr(update, "message", None):
          await update.message.reply_text(pending_text + SIGNATURE)
      elif getattr(update, "callback_query", None):
          await update.callback_query.message.reply_text(pending_text + SIGNATURE)
      return

  try:
      if uid and uid in DATA_START.get("sellers", {}):
          lang = "en"
          context.user_data["lang"] = "en"
  except Exception:
      pass

  sellers_map = DATA_START.get("sellers", {})
  is_seller = False
  try:
      if uid in sellers_map:
          is_seller = True
      elif uid and uid.isdigit() and int(uid) in sellers_map:
          is_seller = True
  except Exception:
      pass

  menu_items = [button_texts["buy"][lang], button_texts["balance"][lang], button_texts["activity"][lang]]
  if uid in admins:
      menu_items.append(button_texts["admin"][lang])
  reply_keyboard = build_rows(menu_items, 2)

  try:
      if is_seller:
          for btn in DATA_START.get("seller_custom_buttons", []):
              label = btn.get("label") if isinstance(btn, dict) else None
              if label:
                  reply_keyboard.append([label])
  except Exception:
      pass

  reply_keyboard.append([button_texts["get_files"][lang]])
  reply_keyboard.append(["⬅️ Back"])

  text = "Welcome to the Sales Bot! Please choose an option:" if lang == "en" else "مرحباً بك في بوت المبيعات! اختر خياراً:"
  if getattr(update, "message", None):
      try:
          DATA_START["start_clicks"] = DATA_START.get("start_clicks", 0) + 1
          save_data(DATA_START)
      except Exception:
          pass
      await update.message.reply_text(text + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
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


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  try:
      await query.answer()
  except telegram.error.BadRequest as e:
      if "Query is too old" in str(e) or "query id is invalid" in str(e):
          return
      print(f"CallbackQuery answer error: {e}")
      return
  except Exception as e:
      print(f"CallbackQuery answer unexpected error: {e}")
      return

  data = getattr(query, "data", None)
  DATA = load_data()
  PRICES = load_prices()
  uid = str(query.from_user.id)
  admins = set(DATA.get("admins", []))
  approved = set(DATA.get("approved_users", []))

  try:
      if uid in DATA.get("sellers", {}):
          context.user_data["lang"] = "en"
  except Exception:
      pass

  if uid not in admins and uid not in approved:
      await query.edit_message_text("⏳ Your access request is pending admin approval." + SIGNATURE)
      return
  if data and data.startswith("admin_") and uid not in admins:
      await query.edit_message_text("❌ Permission denied." + SIGNATURE)
      return

  if data == "back_to_start":
      lang = context.user_data.get("lang", "en")
      menu_text = "Welcome to the Sales Bot! Please choose an option:" if lang == "en" else "مرحباً بك في بوت المبيعات! اختر خياراً:"
      menu_items = ["🛍️ BUY KEYS" if lang == "en" else "🛍️ شراء مفاتيح", "💰 MY BALANCE" if lang == "en" else "💰 رصيدي", "📊 Activity" if lang == "en" else "📊 النشاط"]
      if uid in admins:
          menu_items.append("🔐 ADMIN PANEL" if lang == "en" else "🔐 لوحة الادمن")
      reply_keyboard = build_rows(menu_items, 2)
      try:
          if uid in DATA.get("sellers", {}):
              lang = "en"
              menu_text = "Welcome to the Sales Bot! Please choose an option:"
              for btn in DATA.get("seller_custom_buttons", []):
                  label = btn.get("label") if isinstance(btn, dict) else None
                  if label:
                      reply_keyboard.append([label])
      except Exception:
          pass
      reply_keyboard.append(["📁 Get Files" if lang == "en" else "📁 الحصول على الملفات"])
      reply_keyboard.append(["⬅️ Back"])
      lang_val = context.user_data.get("lang")
      context.user_data.clear()
      if lang_val:
          context.user_data["lang"] = lang_val
      await query.edit_message_text(menu_text + SIGNATURE)
      await query.message.reply_text(menu_text + SIGNATURE, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      return

  if data == "admin_menu":
      if uid not in admins:
          await query.edit_message_text("❌ Permission denied." + SIGNATURE)
          return
      admin_keyboard = [
          [InlineKeyboardButton("💳 Add Balance", callback_data="admin_add_balance")],
          [InlineKeyboardButton("💸 Withdraw", callback_data="admin_withdraw")],
          [InlineKeyboardButton("🔑 Add Keys", callback_data="admin_add_keys")],
          [InlineKeyboardButton("💲 Edit Seller Prices", callback_data="admin_edit_prices")],
          [InlineKeyboardButton("📥 Upload Product File", callback_data="admin_upload_file")],
          [InlineKeyboardButton("📤 Send File to User", callback_data="admin_send_file_to_user")],
          [InlineKeyboardButton("➕ Add Seller", callback_data="admin_add_seller_cb")],
          [InlineKeyboardButton("➖ Remove Seller", callback_data="admin_remove_seller_cb")],
          [InlineKeyboardButton("📋 List Sellers", callback_data="admin_list_sellers")],
          [InlineKeyboardButton("💰 Sellers Balance", callback_data="admin_sellers")],
          [InlineKeyboardButton("🔑 Available Keys", callback_data="admin_available_keys")],
          [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
          [InlineKeyboardButton("💾 Export Backup", callback_data="admin_export_backup")],
          [InlineKeyboardButton("✅ Pending Users", callback_data="admin_pending_users")],
          [InlineKeyboardButton("📝 آخر عمليات الشراء", callback_data="admin_last_sales")],
          [InlineKeyboardButton("📊 Activity", callback_data="show_activity")],
          [InlineKeyboardButton("🧾 جميع أرصدة اللاعبين", callback_data="admin_all_balances")],
          [InlineKeyboardButton("🗝️ سحب المفاتيح", callback_data="admin_withdraw_keys")],
          [InlineKeyboardButton("🗂️ جميع المفاتيح والعوائد", callback_data="admin_keys_revenue")],
          [InlineKeyboardButton("📄 Full Report (TXT)", callback_data="admin_report")],
          [InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]
      ]
      await query.edit_message_text("قائمة الأدمن:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(admin_keyboard))
      return

  if data == "admin_export_backup":
      try:
          await context.bot.send_document(chat_id=query.from_user.id, document=InputFile(DATA_FILE), filename="bot_data.json")
          await context.bot.send_document(chat_id=query.from_user.id, document=InputFile(PRICES_FILE), filename="prices.json")
          await query.edit_message_text("✅ تم إرسال النسخة الاحتياطية." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      except Exception as e:
          await query.edit_message_text("❌ فشل إرسال النسخة الاحتياطية: " + str(e) + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_pending_users":
      pending = DATA.get("pending_users", [])
      if not pending:
          await query.edit_message_text("لا توجد طلبات معلقة." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      keyboard = []
      for pid in pending[:50]:
          keyboard.append([InlineKeyboardButton(f"✅ Accept {pid}", callback_data=f"admin_approve_user:{pid}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("طلبات الانتظار:", reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_approve_user:"):
      _, target = data.split(":", 1)
      DATA.setdefault("approved_users", [])
      DATA.setdefault("pending_users", [])
      if target not in DATA["approved_users"]:
          DATA["approved_users"].append(target)
      if target in DATA["pending_users"]:
          DATA["pending_users"].remove(target)
      save_data(DATA)
      try:
          await context.bot.send_message(chat_id=int(target), text="✅ Your access has been approved." + SIGNATURE)
      except Exception:
          pass
      await query.edit_message_text(f"✅ Approved {target}." + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_all_balances":
      balances = DATA.get("balances", {})
      users = DATA.get("users", [])
      msg = "🧾 جميع أرصدة اللاعبين:\n\n"
      for uid_item in users:
          bal = balances.get(uid_item, 0)
          msg += f"• {uid_item}: ${bal}\n"
      await query.edit_message_text(msg + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "buy_menu":
      lang = context.user_data.get("lang", "en")
      product_names = {
          "FREE": {"en": "🔮 FREE FIRE", "ar": "🔮 فري فاير"},
          "WIZARD": {"en": "✨ WIZARD", "ar": "✨ ويزارد"},
          "BUY_CERT": {"en": "🎖️ BUY CERT", "ar": "🎖️ شراء شهادة"},
          "CLOUD": {"en": "☁️ CLOUD", "ar": "☁️ كلاود"},
          "CODM_IOS": {"en": "📱 CODM IOS", "ar": "📱 كودم IOS"},
          "TERMINAL_X_PC": {"en": "💻 TERMINAL X PC", "ar": "💻 تيرمنال X PC"},
          "HG_CHEATS_ROOT": {"en": "🛡️ HG CHEATS ROOT", "ar": "🛡️ HG شيتس روت"}
      }
      buttons = [product_names[p][lang] for p in product_names]
      reply_keyboard = build_rows(buttons, 2)
      reply_keyboard.append(["⬅️ Back"])
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

  if data == "show_activity":
      DATA_STAT = load_data()
      uid = str(query.from_user.id)
      admins = set(DATA_STAT.get("admins", []))
      sellers_map = DATA_STAT.get("sellers", {})
      is_seller = uid in sellers_map or (uid.isdigit() and int(uid) in sellers_map)
      if uid not in admins and not is_seller:
          msg = build_customer_activity_message(DATA_STAT, uid)
          await query.edit_message_text(msg + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
          return

      if is_seller:
          seller = sellers_map.get(uid, {}) if uid in sellers_map else sellers_map.get(int(uid), {})
          balance = seller.get("balance", 0)
          sales = [s for s in DATA_STAT.get("sales_log", []) if str(s.get("seller_id")) == str(uid)]
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

  if data == "dismiss_seller_promo":
      try:
          await query.edit_message_text("Promo dismissed." + SIGNATURE)
      except Exception:
          pass
      return

  if data and data.startswith("buy:"):
      product = data.split(":", 1)[1]
      user_id = str(query.from_user.id)
      show_prices = user_id in DATA.get("balances", {})
      prod_prices = PRICES.get("global", {}).get(product)
      if not prod_prices:
          await query.edit_message_text(f"⚠️ No pricing/config found for {product}. Ask the admin to set prices or add keys." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="buy_menu")]]))
          return
      keyboard = []
      for days in sorted(prod_prices.keys(), key=lambda x: int(x)):
          # Get user-specific or global price
          price = get_price_for_user(PRICES, product, days, user_id, DATA)
          btn_text = f"⏱️ {days}يوم - ${price}" if show_prices else f"⏱️ {days}يوم"
          keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"choose_qty:{product}:{days}")])
      keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="buy_menu")])
      if show_prices:
          await query.edit_message_text(f"اختر المدة للمنتج {product}:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      else:
          await query.edit_message_text(f"اختر المدة للمنتج {product}:\n(سيتم عرض الأسعار بعد إضافتك من قبل الأدمن)" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("choose_qty:"):
      _, product, days = data.split(":", 2)
      qty_keyboard = [[InlineKeyboardButton(str(i), callback_data=f"pay:{product}:{days}:{i}")] for i in range(1, 11)]
      qty_keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"buy:{product}")])
      await query.edit_message_text(f"Select quantity for {product} ({days} days):" + SIGNATURE, reply_markup=InlineKeyboardMarkup(qty_keyboard))
      return

  if data and data.startswith("pay:"):
      parts = data.split(":")
      product = parts[1]
      days = parts[2]
      qty = int(parts[3]) if len(parts) > 3 else 1
      unit_price = PRICES.get("global", {}).get(product, {}).get(days)
      if unit_price is None:
          await query.edit_message_text(
              f"⚠️ Pricing not configured for {product} {days} days." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buy_menu")]])
          )
          return
      price = unit_price * qty
      user_id = str(query.from_user.id)
      try:
          balance = float(DATA.get("balances", {}).get(user_id, 0))
      except Exception:
          balance = 0
      key_name = key_storage_name(product, days)
      keys_pool = [k for k in DATA.get("keys", {}).get(key_name, []) if k not in set(DATA.get("used_keys", []))]
      if balance < price:
          await query.edit_message_text(
              f"❌ Insufficient balance!\nPrice: ${price}\nYour balance: ${balance}" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buy_menu")]])
          )
          return
      if len(keys_pool) < qty:
          await query.edit_message_text(
              f"❌ Not enough keys available for {product} - {days} days, quantity {qty}.\nAvailable: {len(keys_pool)}\nExpected key bucket: {key_name}\nAsk admin to add keys for this exact product/duration." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buy_menu")]])
          )
          return
      keys = [keys_pool.pop(0) for _ in range(qty)]
      DATA.setdefault("used_keys", [])
      DATA["used_keys"] = list(set(DATA.get("used_keys", [])).union(keys))
      DATA.setdefault("keys", {})[key_name] = keys_pool
      DATA.setdefault("sold_keys", {}).setdefault(key_name, []).extend(keys)
      DATA.setdefault("balances", {})[user_id] = DATA.get("balances", {}).get(user_id, 0) - price
      seller_id = str(query.from_user.id) if str(query.from_user.id) in DATA.get("sellers", {}) else None
      seller_name = DATA.get("sellers", {}).get(seller_id, {}).get("name", "?") if seller_id else None
      for k in keys:
          sale_entry = {"user": user_id, "product": product, "duration": days, "price": unit_price, "key": k}
          if seller_id:
              sale_entry["seller_id"] = seller_id
              sale_entry["seller_name"] = seller_name
          DATA.setdefault("sales_log", []).append(sale_entry)
      admins = DATA.get("admins", [])
      seller_balance = DATA.get("balances", {}).get(seller_id, 0) if seller_id else None
      buyer_username = query.from_user.username
      buyer_handle = f"@{buyer_username}" if buyer_username else "(no username)"
      keys_str_admin = "\n".join(keys)
      for admin_id in admins:
          try:
              if seller_id:
                  msg_text = (
                      f"🔔 تم بيع مفاتيح!\n"
                      f"المنتج: {product}\n"
                      f"المدة: {days} يوم\n"
                      f"الكمية: {len(keys)}\n"
                      f"المشتري: {buyer_handle} ({user_id})\n"
                      f"المفاتيح:\n{keys_str_admin}\n"
                      f"البائع: {seller_name} ({seller_id})\n"
                      f"الرصيد الحالي للبائع: ${seller_balance}"
                  )
              else:
                  msg_text = (
                      f"🔔 تم شراء مفاتيح\n"
                      f"المنتج: {product}\n"
                      f"المدة: {days} يوم\n"
                      f"الكمية: {len(keys)}\n"
                      f"المشتري: {buyer_handle} ({user_id})\n"
                      f"المفاتيح:\n{keys_str_admin}"
                  )
              await context.bot.send_message(chat_id=int(admin_id), text=msg_text)
          except Exception:
              pass
      save_data(DATA)
      if product.startswith("CERT_"):
          sent, err = send_cert_keys_via_firstone(user_id, keys, SIGNATURE)
          if sent:
              await query.edit_message_text(
                  "✅ Your CERT key was sent via @firstone." + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buy_menu")]])
              )
          else:
              keys_str = "\n".join([f"`{k}`" for k in keys])
              await query.edit_message_text(
                  f"⚠️ Delivery via @firstone failed ({err}).\n\nYour keys:\n{keys_str}\n\n📁 Use Get Files to download product updates." + SIGNATURE,
                  parse_mode="Markdown",
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buy_menu")]])
              )
      else:
          keys_str = "\n".join([f"`{k}`" for k in keys])
          await query.edit_message_text(
              f"✅ Purchase successful!\n\nYour keys:\n{keys_str}\n\n📁 Use Get Files to download product updates." + SIGNATURE,
              parse_mode="Markdown",
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="buy_menu")]])
          )
      return

  if data == "admin_add_keys":
      keyboard = [[InlineKeyboardButton(prod, callback_data=f"admin_add_keys_product:{prod}")] for prod in PRICES.get("global", {}).keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("اختر المنتج لإضافة المفاتيح:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_add_keys_product:"):
      _, prod = data.split(":", 1)
      durations = list(PRICES.get("global", {}).get(prod, {}).keys())
      if not durations:
          await query.edit_message_text(
              f"لا يوجد مدد معرفة لهذا المنتج {prod}. أضف مدد أولاً من الأسعار." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")]])
          )
          return
      keyboard = [[InlineKeyboardButton(f"{d} يوم", callback_data=f"admin_add_keys_duration:{prod}:{d}")] for d in durations]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")])
      await query.edit_message_text(
          f"اختر المدة لإضافة المفاتيح لـ {prod}:" + SIGNATURE,
          reply_markup=InlineKeyboardMarkup(keyboard)
      )
      return

  if data and data.startswith("admin_add_keys_duration:"):
      _, prod, days = data.split(":", 2)
      context.user_data.clear()
      context.user_data["admin_action"] = "add_keys"
      context.user_data["add_keys_product"] = prod
      context.user_data["add_keys_duration"] = days
      await query.edit_message_text(
          f"أرسل المفاتيح (كل مفتاح في سطر) ليتم إضافتها للمنتج {prod} لمدة {days} يوم." + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")]])
      )
      return

  if data == "vip_menu":
      vip_keyboard = [
          [InlineKeyboardButton("➕ إضافة خيار للبائعين", callback_data="vip_add_seller_option")],
          [InlineKeyboardButton("📋 عرض خيارات البائعين", callback_data="vip_list_seller_options")],
          [InlineKeyboardButton("🗑️ حذف كل الخيارات", callback_data="vip_clear_seller_options")],
          [InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]
      ]
      await query.edit_message_text("⭐ لوحة VIP:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(vip_keyboard))
      return

  if data == "vip_add_seller_option":
      context.user_data.clear()
      context.user_data["admin_action"] = "vip_add_seller_option"
      await query.edit_message_text(
          "أرسل النص بهذا الشكل:\nالعنوان | الرد\nمثال: أسعار جديدة | تواصل مع الأدمن" + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="vip_menu")]])
      )
      return

  if data == "vip_list_seller_options":
      opts = DATA.get("seller_custom_buttons", [])
      if not opts:
          await query.edit_message_text(
              "لا توجد خيارات مضافة." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="vip_menu")]])
          )
          return
      msg = "خيارات البائعين الحالية:\n\n"
      for o in opts:
          if isinstance(o, dict):
              msg += f"• {o.get('label','?')} → {o.get('response','')}\n"
      await query.edit_message_text(
          msg + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="vip_menu")]])
      )
      return

  if data == "vip_clear_seller_options":
      DATA["seller_custom_buttons"] = []
      save_data(DATA)
      await query.edit_message_text(
          "تم حذف جميع الخيارات." + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="vip_menu")]])
      )
      return

  if data == "admin_download_keys":
      import tempfile
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
      try:
          os.remove(temp_path)
      except Exception:
          pass
      await query.edit_message_text("تم إرسال ملف جميع المفاتيح المتوفرة لك." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_view_keys":
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

  if data == "admin_available_keys":
      keys_data = DATA.get("keys", {})
      used_keys = set(DATA.get("used_keys", []))
      if not keys_data:
          await query.edit_message_text("لا توجد أي مفاتيح متوفرة حالياً." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      msg = "🔑 Available keys:\n\n"
      total_available = 0
      for prod_dur, keys in keys_data.items():
          available = [k for k in keys if k not in used_keys]
          total_available += len(available)
          msg += f"{prod_dur} ({len(available)}):\n"
          if available:
              for k in available:
                  msg += f"- `{k}`\n"
          else:
              msg += "(no available keys)\n"
          msg += "\n"
      msg += f"Total available: {total_available}"
      await query.edit_message_text(msg + SIGNATURE, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_list_sellers":
      sellers = DATA.get("sellers", {})
      if not sellers:
          await query.edit_message_text("No sellers configured." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      msg = "📋 Sellers list:\n\n"
      sales_log = DATA.get("sales_log", [])
      for sid, info in sellers.items():
          seller_balance = info.get("balance", 0)
          wallet_balance = DATA.get("balances", {}).get(str(sid), 0)
          if wallet_balance != seller_balance:
              msg += f"- {info.get('name','?')} ({sid}) — Balance: ${seller_balance} | Wallet: ${wallet_balance}\n"
          else:
              msg += f"- {info.get('name','?')} ({sid}) — Balance: ${seller_balance}\n"
          seller_sales = [s for s in sales_log if str(s.get("seller_id")) == str(sid)]
          if not seller_sales:
              msg += "Keys: (none)\n\n"
              continue
          msg += "Keys by product:\n"
          by_product = {}
          for s in seller_sales:
              product = s.get("product", "?")
              duration = s.get("duration", "?")
              key = s.get("key")
              duration_str = str(duration)
              if duration_str in {"30", "31"}:
                  dur_label = "month"
              elif duration_str == "7":
                  dur_label = "week"
              elif duration_str == "1":
                  dur_label = "day"
              else:
                  dur_label = f"{duration_str} days"
              label = f"{product} {dur_label}"
              by_product.setdefault(label, [])
              if key:
                  by_product[label].append(key)
          for label, keys in by_product.items():
              if not keys:
                  msg += f"- {label}: (no keys stored)\n"
              else:
                  for k in keys:
                      msg += f"- {label}: `{k}`\n"
          msg += "\n"
      await query.edit_message_text(
          msg + SIGNATURE,
          parse_mode="Markdown",
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]])
      )
      return

  if data == "admin_last_sales":
      sales = DATA.get("sales_log", [])[-20:]
      if not sales:
          await query.edit_message_text("No sales yet." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      msg = "📝 Last purchases:\n\n"
      for s in sales:
          buyer = s.get("user")
          product = s.get("product")
          duration = s.get("duration")
          price = s.get("price")
          msg += f"- {buyer} | {product} | {duration} days | ${price}\n"
      await query.edit_message_text(msg + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_keys_revenue":
      sales = DATA.get("sales_log", [])
      if not sales:
          await query.edit_message_text("No sales yet." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      total_revenue = 0
      by_product = {}
      for s in sales:
          product = s.get("product")
          price = s.get("price")
          by_product.setdefault(product, {"count": 0, "revenue": 0})
          by_product[product]["count"] += 1
          try:
              by_product[product]["revenue"] += float(price)
              total_revenue += float(price)
          except Exception:
              pass
      msg = "🗂️ Keys & revenue:\n\n"
      for product, info in by_product.items():
          msg += f"- {product}: {info['count']} keys — ${info['revenue']}\n"
      msg += f"\nTotal revenue: ${total_revenue}"
      await query.edit_message_text(msg + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_edit_prices":
      keyboard = [[InlineKeyboardButton(prod, callback_data=f"edit_price:{prod}")] for prod in PRICES.get("global", {}).keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Select product to edit prices for:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("edit_price:"):
      _, prod = data.split(":", 1)
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
      sellers = DATA.get("sellers", {})
      if not sellers:
          await query.edit_message_text("No sellers configured." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_edit_prices")]]))
          return
      keyboard = [[InlineKeyboardButton("GLOBAL", callback_data=f"edit_price_choose_seller:{prod}:{days}:global")]]
      for sid, info in sellers.items():
          keyboard.append([InlineKeyboardButton(f"{info.get('name','?')} ({sid})", callback_data=f"edit_price_choose_seller:{prod}:{days}:{sid}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_edit_prices")])
      await query.edit_message_text(f"Select seller for {prod} ({days} days):" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("edit_price_choose_seller:"):
      _, prod, days, seller_id = data.split(":", 3)
      context.user_data["admin_action"] = "set_price"
      context.user_data["edit_price_product"] = prod
      context.user_data["edit_price_days"] = days
      context.user_data["edit_price_seller"] = seller_id
      await query.edit_message_text(
          f"Send new price for {prod} ({days} days) for {'GLOBAL' if seller_id == 'global' else seller_id}:" + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_edit_prices")]])
      )
      return

  if data == "admin_create_key":
      keyboard = [[InlineKeyboardButton(prod, callback_data=f"admin_create_key_product:{prod}")] for prod in PRICES.get("global", {}).keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Select product to create a single key for:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_create_key_product:"):
      _, prod = data.split(":", 1)
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

  if data == "admin_sellers":
      sellers = DATA.get("sellers", {})
      if not sellers:
          await query.edit_message_text("No sellers configured." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      keyboard = []
      for sid, info in sellers.items():
          seller_balance = info.get("balance", 0)
          wallet_balance = DATA.get("balances", {}).get(str(sid), 0)
          if wallet_balance != seller_balance:
              label = f"{info.get('name','?')} - {sid} - ${seller_balance} | Wallet ${wallet_balance}"
          else:
              label = f"{info.get('name','?')} - {sid} - ${seller_balance}"
          keyboard.append([InlineKeyboardButton(label, callback_data=f"admin_seller:{sid}")])
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("Sellers:", reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_seller:"):
      _, sid = data.split(":", 1)
      s = DATA.get("sellers", {}).get(sid)
      if not s:
          await query.edit_message_text("Seller not found." + SIGNATURE)
          return
      seller_balance = s.get("balance", 0)
      wallet_balance = DATA.get("balances", {}).get(str(sid), 0)
      keyboard = [[InlineKeyboardButton("Add Balance", callback_data=f"admin_add_seller_balance:{sid}")], [InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]
      await query.edit_message_text(
          f"Seller {s.get('name')} (ID: {sid})\nBalance: ${seller_balance}\nWallet: ${wallet_balance}\nSales: {s.get('sales_count',0)}" + SIGNATURE,
          reply_markup=InlineKeyboardMarkup(keyboard)
      )
      return

  if data and data.startswith("admin_add_seller_balance:"):
      _, sid = data.split(":", 1)
      context.user_data["admin_action"] = "add_seller_balance"
      context.user_data["target_seller"] = sid
      await query.edit_message_text(f"Send amount to add to seller {sid}:" + SIGNATURE)
      return

  if data == "admin_broadcast":
      context.user_data["admin_action"] = "broadcast"
      await query.edit_message_text("Send the broadcast message to deliver to all known users:" + SIGNATURE)
      return

  if data == "admin_add_balance":
      context.user_data.clear()
      context.user_data["admin_action"] = "add_balance"
      await query.edit_message_text("أدخل معرف المستخدم والمبلغ (مثال: 123456789 10)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_upload_file":
      keyboard = [[InlineKeyboardButton(prod, callback_data=f"admin_upload_file_product:{prod}")] for prod in PRICES.get("global", {}).keys()]
      keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")])
      await query.edit_message_text("اختر المنتج لرفع الملف:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(keyboard))
      return

  if data and data.startswith("admin_upload_file_product:"):
      _, prod = data.split(":", 1)
      context.user_data.clear()
      context.user_data["admin_action"] = "upload_file"
      context.user_data["upload_product"] = prod
      await query.edit_message_text(f"أرسل الملف للمنتج {prod}." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_send_file_to_user":
      context.user_data.clear()
      context.user_data["admin_action"] = "send_file_to_user"
      await query.edit_message_text("أدخل معرف المستخدم لإرسال الملف له (مثال: 123456789)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_withdraw":
      context.user_data.clear()
      context.user_data["admin_action"] = "withdraw"
      await query.edit_message_text("أدخل معرف المستخدم والمبلغ للسحب (مثال: 123456789 5)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return

  if data == "admin_withdraw_keys":
      context.user_data.clear()
      context.user_data["admin_action"] = "withdraw_keys"
      await query.edit_message_text("أدخل المنتج والمدة والكمية (مثال: FREE 7 2)" + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
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
      files = DATA.get("files", {})
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
      file_ref = DATA.get("files", {}).get(prod)
      if not file_ref:
          await query.edit_message_text("File not found." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
          return
      try:
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
          await query.edit_message_text(f"File {prod} sent to you." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
      except Exception as e:
          await query.edit_message_text("Failed to send file: " + str(e) + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
      return

  if data and data.startswith("admin_delete_file:"):
      _, prod = data.split(":", 1)
      files = DATA.get("files", {})
      if prod not in files:
          await query.edit_message_text("File not found." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
          return
      file_ref = files.get(prod)
      try:
          if os.path.exists(file_ref):
              os.remove(file_ref)
      except Exception:
          pass
      DATA.get("files", {}).pop(prod, None)
      if "files_meta" in DATA:
          DATA.get("files_meta", {}).pop(prod, None)
      save_data(DATA)
      await query.edit_message_text(f"Deleted file for product {prod}." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_manage_files")]]))
      return

  if data and data.startswith("seller_get_file:"):
      _, prod = data.split(":", 1)
      if uid not in DATA.get("sellers", {}):
          await query.edit_message_text("Only sellers can download product files." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
          return
      file_ref = DATA.get("files", {}).get(prod)
      if not file_ref:
          await query.edit_message_text("No file uploaded for this product." + SIGNATURE, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
          return
      try:
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


async def send_duration_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_product: str, lang: str, lang_button_text: str):
  PRICES = load_prices()
  durations = list(PRICES.get("global", {}).get(selected_product, {}).keys())
  if not durations:
      await update.message.reply_text(f"⚠️ لا توجد أسعار معرفة للمنتج {selected_product}. تواصل مع الأدمن." + SIGNATURE)
      return False
  duration_names = {
      "1": {"en": "1 day", "ar": "يوم", "fr": "1 jour", "es": "1 día", "de": "1 Tag", "tr": "1 gün"},
      "3": {"en": "3 days", "ar": "3 أيام", "fr": "3 jours", "es": "3 días", "de": "3 Tage", "tr": "3 gün"},
      "7": {"en": "7 days", "ar": "7 أيام", "fr": "7 jours", "es": "7 días", "de": "7 Tage", "tr": "7 gün"},
      "10": {"en": "10 days", "ar": "10 أيام", "fr": "10 jours", "es": "10 días", "de": "10 Tage", "tr": "10 gün"},
      "15": {"en": "15 days", "ar": "15 يوم", "fr": "15 jours", "es": "15 días", "de": "15 Tage", "tr": "15 gün"},
      "30": {"en": "30 days", "ar": "30 يوم", "fr": "30 jours", "es": "30 días", "de": "30 Tage", "tr": "30 gün"},
      "31": {"en": "1 month", "ar": "شهر", "fr": "1 mois", "es": "1 mes", "de": "1 Monat", "tr": "1 ay"},
      "365": {"en": "1 year", "ar": "سنة", "fr": "1 an", "es": "1 año", "de": "1 Jahr", "tr": "1 yıl"}
  }
  reply_keyboard = []
  for d in durations:
      if d in duration_names:
          price = PRICES.get("global", {}).get(selected_product, {}).get(d)
          if price is not None:
              reply_keyboard.append([f"{duration_names[d][lang]} - ${price}"])
          else:
              reply_keyboard.append([duration_names[d][lang]])
  reply_keyboard.append(["⬅️ Back"])
  await update.message.reply_text(
      "اختر المدة:" if lang == "ar" else
      "Select duration:" if lang == "en" else
      "Sélectionnez la durée:" if lang == "fr" else
      "Seleccione la duración:" if lang == "es" else
      "Dauer auswählen:" if lang == "de" else
      "Süre seçin:",
      reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
  )
  context.user_data["selected_product"] = selected_product
  context.user_data["choose_duration"] = True
  context.user_data["buy_menu"] = False
  return True


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = update.message.text.strip() if update.message.text else ""
  uid = str(update.message.from_user.id)
  if not context.user_data.get("lang"):
      context.user_data["lang"] = DEFAULT_LANG

  try:
      DATA_LOCAL = load_data()
      if uid not in DATA_LOCAL.get("users", []):
          DATA_LOCAL.setdefault("users", []).append(uid)
          save_data(DATA_LOCAL)
  except Exception:
      pass

  try:
      DATA_APPROVE = load_data()
      admins = set(DATA_APPROVE.get("admins", []))
      approved = set(DATA_APPROVE.get("approved_users", []))
      if uid not in admins and uid not in approved and text != ADMIN_CODE:
          DATA_APPROVE.setdefault("pending_users", [])
          if uid not in DATA_APPROVE["pending_users"]:
              DATA_APPROVE["pending_users"].append(uid)
              save_data(DATA_APPROVE)
          await update.message.reply_text("⏳ Your access request is pending admin approval." + SIGNATURE)
          return
  except Exception:
      pass

  try:
      DATA_LANG = load_data()
      if uid in DATA_LANG.get("sellers", {}):
          context.user_data["lang"] = "en"
  except Exception:
      pass

  if context.user_data.get("admin_action") == "withdraw_keys":
      try:
          parts = text.split()
          product, duration, qty = parts[0], parts[1], int(parts[2])
          data = load_data()
          key_name = f"{product}_{duration}"
          keys_pool = data.get("keys", {}).get(key_name, [])
          used_keys = set(data.get("used_keys", []))
          available = [k for k in keys_pool if k not in used_keys]
          if len(available) < qty:
              await update.message.reply_text(f"❌ لا يوجد مفاتيح كافية للسحب. المتوفر: {len(available)}" + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
              return
          withdrawn = available[:qty]
          data.setdefault("used_keys", [])
          data["used_keys"] = list(set(data.get("used_keys", [])).union(withdrawn))
          data.setdefault("sold_keys", {}).setdefault(key_name, []).extend(withdrawn)
          save_data(data)
          keys_str = "\n".join([f"`{k}`" for k in withdrawn])
          await update.message.reply_text(f"✅ تم سحب المفاتيح:\n{keys_str}" + SIGNATURE, parse_mode="Markdown",
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          context.user_data.pop("admin_action", None)
      except Exception:
          await update.message.reply_text("❌ صيغة خاطئة. مثال: FREE 7 2" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          context.user_data.pop("admin_action", None)
      return

  try:
      DATA_BTN = load_data()
      if uid in DATA_BTN.get("sellers", {}):
          for o in DATA_BTN.get("seller_custom_buttons", []):
              if isinstance(o, dict) and text == o.get("label"):
                  await update.message.reply_text((o.get("response") or "") + SIGNATURE)
                  return
  except Exception:
      pass

  if update.message.document and context.user_data.get("admin_action") in ("upload_file", "send_file_to_user_upload"):
      if context.user_data.get("admin_action") == "send_file_to_user_upload":
          target_uid = context.user_data.get("target_user")
          if not target_uid:
              await update.message.reply_text("No target user set." + SIGNATURE)
          else:
              try:
                  await context.bot.send_document(chat_id=int(target_uid), document=update.message.document)
                  await update.message.reply_text("✅ File sent to user." + SIGNATURE)
              except Exception as e:
                  await update.message.reply_text("Failed to send file: " + str(e) + SIGNATURE)
          context.user_data.pop("admin_action", None)
          context.user_data.pop("target_user", None)
          return

      prod = context.user_data.get("upload_product")
      if not prod:
          await update.message.reply_text("No product selected for file upload." + SIGNATURE)
      else:
          DATA2 = load_data()
          try:
              files_dir = os.path.join(os.getcwd(), "files")
              os.makedirs(files_dir, exist_ok=True)
              doc = update.message.document
              file_id = doc.file_id
              original_name = getattr(doc, "file_name", None) or f"{prod}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.dat"
              safe_name = original_name.replace("/", "_").replace("\\", "_")
              local_path = os.path.join(files_dir, safe_name)
              tg_file = await context.bot.get_file(file_id)
              await tg_file.download_to_drive(local_path)
              rel_path = os.path.relpath(local_path, os.getcwd())
              DATA2.setdefault("files", {})[prod] = rel_path
              DATA2.setdefault("files_meta", {})[prod] = {"tg_file_id": file_id, "local": rel_path}
              save_data(DATA2)
              await update.message.reply_text(f"File saved for product {prod} to {rel_path}." + SIGNATURE)
          except Exception as e:
              await update.message.reply_text("Failed to save file: " + str(e) + SIGNATURE)
      context.user_data.pop("admin_action", None)
      context.user_data.pop("upload_product", None)
      return

  if context.user_data.get("admin_action") == "vip_add_seller_option":
      DATA_VIP = load_data()
      raw = text
      if "|" in raw:
          label, response = [p.strip() for p in raw.split("|", 1)]
      else:
          label, response = raw.strip(), raw.strip()
      if not label:
          await update.message.reply_text("❌ الصيغة غير صحيحة." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="vip_menu")]]))
          context.user_data.pop("admin_action", None)
          return
      DATA_VIP.setdefault("seller_custom_buttons", [])
      DATA_VIP["seller_custom_buttons"].append({"label": label, "response": response})
      save_data(DATA_VIP)
      await update.message.reply_text("✅ تم إضافة الخيار بنجاح." + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="vip_menu")]]))
      context.user_data.pop("admin_action", None)
      return

  lang = context.user_data.get("lang", "en")
  button_texts = {
      "buy": {"en": "🛍️ BUY KEYS", "ar": "🛍️ شراء مفاتيح"},
      "balance": {"en": "💰 MY BALANCE", "ar": "💰 رصيدي"},
      "admin": {"en": "🔐 ADMIN PANEL", "ar": "🔐 لوحة الادمن"},
      "activity": {"en": "📊 Activity", "ar": "📊 النشاط"},
      "get_files": {"en": "📁 Get Files", "ar": "📁 الحصول على الملفات"}
  }

  if text == "⬅️ Back":
      context.user_data.clear()
      await start(update, context)
      return

  if text == button_texts["balance"][lang]:
      data = load_data()
      bal = data.get("balances", {}).get(uid, 0)
      await update.message.reply_text((f"Your balance: ${bal}" if lang == "en" else f"رصيدك: ${bal}") + SIGNATURE)
      return

  if text == button_texts["admin"][lang]:
      await update.message.reply_text("Enter admin code:" + SIGNATURE)
      context.user_data["awaiting_admin_code"] = True
      return

  if context.user_data.get("awaiting_admin_code"):
      if text == ADMIN_CODE:
          context.user_data.pop("awaiting_admin_code", None)
          try:
              DATA_AD = load_data()
              DATA_AD.setdefault("admins", [])
              if uid not in DATA_AD["admins"]:
                  DATA_AD["admins"].append(uid)
                  save_data(DATA_AD)
          except Exception:
              pass
          await update.message.reply_text("👍 Admin panel access granted." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Main Menu", callback_data="admin_menu")]]))
      else:
          await update.message.reply_text("❌ Wrong code!" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_start")]]))
      return

  if text == button_texts["get_files"][lang]:
      DATAF = load_data()
      files = DATAF.get("files", {})
      if uid in DATAF.get("sellers", {}):
          available = list(files.keys())
      else:
          purchases = [s.get("product") for s in DATAF.get("sales_log", []) if s.get("user") == uid]
          available = sorted(set(purchases))
      if not available:
          await update.message.reply_text("No files available for you." + SIGNATURE)
          return
      reply_keyboard = [[p] for p in available]
      reply_keyboard.append(["⬅️ Back"])
      await update.message.reply_text("Select product to download file:" + SIGNATURE,
          reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      context.user_data["getting_file"] = True
      return

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
                  allowed = False
                  if uid in DATAF.get("sellers", {}):
                      allowed = True
                  else:
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

  if text == button_texts["buy"][lang]:
      PRICES = load_prices()
      product_names = {
          "FREE": {"en": "🔮 FREE FIRE", "ar": "🔮 فري فاير"},
          "WIZARD": {"en": "✨ WIZARD", "ar": "✨ ويزارد"},
          "BUY_CERT": {"en": "🎖️ BUY CERT", "ar": "🎖️ شراء شهادة"}
      }
      products = list(product_names.keys())
      buttons = [product_names[p][lang] for p in products]
      reply_keyboard = build_rows(buttons, 2)
      reply_keyboard.append(["⬅️ Back"])
      await update.message.reply_text("Select a product:" + SIGNATURE,
          reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
      context.user_data["buy_menu"] = True
      return

  if context.user_data.get("buy_menu"):
      product_names = {
          "FREE": {"en": "🔮 FREE FIRE", "ar": "🔮 فري فاير"},
          "WIZARD": {"en": "WIZARD", "ar": "ويزارد"},
          "BUY_CERT": {"en": "BUY CERT", "ar": "شراء شهادة"}
      }
      selected_product = None
      lower_text = text.lower()
      for key, names in product_names.items():
          display = names[lang]
          if text == display or display in text or key.lower() in lower_text or key in text:
              selected_product = key
              break
      if selected_product:
          if selected_product == "FREE":
              reply_keyboard = [["📱 iOS"], ["🤖 Android"], ["⬅️ Back"]]
              await update.message.reply_text("Select OS:" + SIGNATURE,
                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
              context.user_data["buy_menu"] = False
              context.user_data["choose_free_os"] = True
              return
          if selected_product == "BUY_CERT":
              reply_keyboard = [
                  ["🎖️ 90-Day Warranty - 5 USDT"],
                  ["🎖️ 180-Day Warranty - 8 USDT"],
                  ["🎖️ 300-Day Warranty - 10 USDT"],
                  ["🎖️ 300-Day Warranty (iPad) - 4 USDT"],
                  ["🎖️ Certificate 0 - 4 USDT"],
                  ["🎖️ Certificate 30 - 4 USDT"],
                  ["⬅️ Back"]
              ]
              await update.message.reply_text("Select certificate:" + SIGNATURE,
                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
              context.user_data["buy_menu"] = False
              context.user_data["choose_cert_type"] = True
              return
          await send_duration_menu(update, context, selected_product, lang, "")
          return

  if context.user_data.get("choose_free_os"):
      if "ios" in text.lower():
          reply_keyboard = [["FLUORIT"], ["MIGUL PRO"], ["⬅️ Back"]]
          await update.message.reply_text("Select option:" + SIGNATURE,
              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
          context.user_data["choose_free_os"] = False
          context.user_data["choose_free_variant"] = True
          context.user_data["free_os"] = "ios"
          return
      if "android" in text.lower():
          reply_keyboard = [["DRIP"], ["DRIP CLIENT ROOT DEVICE"], ["HG CHEAT"], ["PATO TEAM"], ["⬅️ Back"]]
          await update.message.reply_text("Select option:" + SIGNATURE,
              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
          context.user_data["choose_free_os"] = False
          context.user_data["choose_free_variant"] = True
          context.user_data["free_os"] = "android"
          return

  if context.user_data.get("choose_free_variant"):
      free_os = context.user_data.get("free_os")
      if free_os == "ios":
          if text.upper() == "FLUORIT":
              context.user_data.pop("choose_free_variant", None)
              context.user_data.pop("free_os", None)
              await send_duration_menu(update, context, "FF_IOS_FLUORIT", lang, "")
              return
          if text.upper() in ("MIGUL PRO", "MUGIL PRO"):
              context.user_data.pop("choose_free_variant", None)
              context.user_data.pop("free_os", None)
              await send_duration_menu(update, context, "FF_IOS_MUGIL_PRO", lang, "")
              return
      if free_os == "android":
          if text.upper() == "DRIP":
              context.user_data.pop("choose_free_variant", None)
              context.user_data.pop("free_os", None)
              await send_duration_menu(update, context, "DRIP", lang, "")
              return
          if text.upper() in ("DRIP CLIENT ROOT DEVICE", "DRIP_CLIENT_ROOT_DEVICE"):
              context.user_data.pop("choose_free_variant", None)
              context.user_data.pop("free_os", None)
              await send_duration_menu(update, context, "DRIP_CLIENT_ROOT_DEVICE", lang, "")
              return
          if text.upper() in ("HG CHEAT", "HG CHEATS", "HG_CHEAT"):
              context.user_data.pop("choose_free_variant", None)
              context.user_data.pop("free_os", None)
              await send_duration_menu(update, context, "HG_CHEAT_ANDROID", lang, "")
              return
          if text.upper() in ("PATO TEAM", "PATO_TEAM"):
              context.user_data.pop("choose_free_variant", None)
              context.user_data.pop("free_os", None)
              await send_duration_menu(update, context, "PATO_TEAM", lang, "")
              return

  if context.user_data.get("choose_cert_type"):
      choice = text.lower()
      cert_product = None
      if "ipad" in choice:
          cert_product = "CERT_300_IPAD"
      elif "certificate 0" in choice or "certificate0" in choice:
          cert_product = "CERT_JIT_0"
      elif "certificate 30" in choice or "certificate30" in choice:
          cert_product = "CERT_JIT_30"
      elif "180" in choice:
          cert_product = "CERT_180"
      elif "90" in choice:
          cert_product = "CERT_90"
      elif "300" in choice:
          cert_product = "CERT_300"
      
      

      if not cert_product:
          await update.message.reply_text("Select certificate:" + SIGNATURE)
          return

      PRICES = load_prices()
      durations = list(PRICES.get("global", {}).get(cert_product, {}).keys())
      if not durations:
          await update.message.reply_text("⚠️ No pricing found for this certificate. Contact admin." + SIGNATURE)
          context.user_data.pop("choose_cert_type", None)
          return

      context.user_data["selected_product"] = cert_product
      context.user_data["selected_duration"] = durations[0]
      context.user_data["choose_cert_type"] = False
      context.user_data["choose_qty"] = True
      qty_keyboard = [[str(i)] for i in range(1, 11)]
      qty_keyboard.append(["⬅️ Back"])
      await update.message.reply_text("Select quantity:" + SIGNATURE,
          reply_markup=ReplyKeyboardMarkup(qty_keyboard, resize_keyboard=True))
      return

  if context.user_data.get("choose_duration"):
      selected_product = context.user_data.get("selected_product")
      PRICES = load_prices()
      durations = list(PRICES.get("global", {}).get(selected_product, {}).keys())
      duration_names = {
          "1": {"en": "1 day", "ar": "يوم"},
          "3": {"en": "3 days", "ar": "3 أيام"},
          "7": {"en": "7 days", "ar": "7 أيام"},
          "10": {"en": "10 days", "ar": "10 أيام"},
          "15": {"en": "15 days", "ar": "15 يوم"},
          "30": {"en": "30 days", "ar": "30 يوم"},
          "31": {"en": "1 month", "ar": "شهر"},
          "365": {"en": "1 year", "ar": "سنة"}
      }
      selected_duration = None
      for d in durations:
          if d in duration_names and duration_names[d][lang] in text:
              selected_duration = d
              break
      if selected_duration:
          reply_keyboard = [[str(i)] for i in range(1, 11)]
          reply_keyboard.append(["⬅️ Back"])
          await update.message.reply_text("Select quantity:" + SIGNATURE,
              reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
          context.user_data["selected_duration"] = selected_duration
          context.user_data["choose_duration"] = False
          context.user_data["choose_qty"] = True
          return

  if context.user_data.get("choose_qty"):
      try:
          qty = int(text)
          if not (1 <= qty <= 10):
              raise ValueError()
      except Exception:
          await update.message.reply_text("Invalid quantity!" + SIGNATURE)
          return
      selected_product = context.user_data.get("selected_product")
      selected_duration = context.user_data.get("selected_duration")
      PRICES = load_prices()
      DATA = load_data()
      unit_price = get_price_for_user(PRICES, selected_product, selected_duration, uid, DATA)
      price = unit_price * qty
      try:
          balance = float(DATA.get("balances", {}).get(uid, 0))
      except Exception:
          balance = 0
      key_name = key_storage_name(selected_product, selected_duration)
      keys_pool = DATA.get("keys", {}).get(key_name, [])
      used_keys = set(DATA.get("used_keys", []))
      keys_pool = [k for k in keys_pool if k not in used_keys]
      if balance < price:
          await update.message.reply_text("❌ Insufficient balance!" + SIGNATURE)
          return
      if len(keys_pool) < qty:
          await update.message.reply_text(
              f"❌ Not enough keys available.\nAvailable: {len(keys_pool)}\nExpected key bucket: {key_name}\nAsk admin to add keys for this exact product/duration." + SIGNATURE
          )
          return
      keys = [keys_pool.pop(0) for _ in range(qty)]
      DATA.setdefault("used_keys", [])
      DATA["used_keys"] = list(set(DATA.get("used_keys", [])).union(keys))
      DATA.setdefault("keys", {})[key_name] = keys_pool
      DATA.setdefault("sold_keys", {}).setdefault(key_name, []).extend(keys)
      DATA.setdefault("balances", {})[uid] = balance - price
      seller_id = uid if uid in DATA.get("sellers", {}) else None
      seller_name = DATA.get("sellers", {}).get(seller_id, {}).get("name", "?") if seller_id else None
      for k in keys:
          sale_entry = {
              "user": uid,
              "product": selected_product,
              "duration": selected_duration,
              "price": unit_price,
              "buyer_balance": balance - price,
              "key": k,
          }
          if seller_id:
              sale_entry["seller_id"] = seller_id
              sale_entry["seller_name"] = seller_name
          DATA.setdefault("sales_log", []).append(sale_entry)
      admins_list = DATA.get("admins", [])
      buyer_balance = balance - price
      buyer_username = update.message.from_user.username
      buyer_handle = f"@{buyer_username}" if buyer_username else "(no username)"
      keys_str_admin = "\n".join(keys)
      for admin_id in admins_list:
          try:
              if seller_id:
                  text_msg = (
                      f"🔔 تم شراء مفاتيح بواسطة بائع\n"
                      f"المنتج: {selected_product}\n"
                      f"المدة: {selected_duration} يوم\n"
                      f"الكمية: {len(keys)}\n"
                      f"المشتري: {buyer_handle} ({uid})\n"
                      f"المفاتيح:\n{keys_str_admin}\n"
                      f"البائع: {seller_name} ({seller_id})\n"
                      f"رصيد المشتري بعد الشراء: ${buyer_balance}"
                  )
              else:
                  text_msg = (
                      f"🔔 تم شراء مفاتيح\n"
                      f"المنتج: {selected_product}\n"
                      f"المدة: {selected_duration} يوم\n"
                      f"الكمية: {len(keys)}\n"
                      f"المشتري: {buyer_handle} ({uid})\n"
                      f"المفاتيح:\n{keys_str_admin}\n"
                      f"رصيد المشتري بعد الشراء: ${buyer_balance}"
                  )
              await context.bot.send_message(chat_id=int(admin_id), text=text_msg)
          except Exception:
              pass
      save_data(DATA)
      if selected_product.startswith("CERT_"):
          sent, err = send_cert_keys_via_firstone(uid, keys, SIGNATURE)
          if sent:
              await update.message.reply_text("✅ Your CERT key was sent via @firstone." + SIGNATURE)
          else:
              keys_str = "\n".join([f"`{k}`" for k in keys])
              await update.message.reply_text(
                  f"⚠️ Delivery via @firstone failed ({err}).\n\nYour keys:\n{keys_str}\n\n📁 Use Get Files to download product updates." + SIGNATURE,
                  parse_mode="Markdown"
              )
      else:
          keys_str = "\n".join([f"`{k}`" for k in keys])
          await update.message.reply_text(
              f"✅ Purchase successful!\n\nYour keys:\n{keys_str}\n\n📁 Use Get Files to download product updates." + SIGNATURE,
              parse_mode="Markdown"
          )
      context.user_data.pop("selected_product", None)
      context.user_data.pop("selected_duration", None)
      context.user_data.pop("choose_qty", None)
      return

  action = context.user_data.get("admin_action")
  if action == "send_file_to_user":
      target_uid = text.strip()
      if not target_uid.isdigit():
          await update.message.reply_text("❌ معرف المستخدم غير صحيح." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          return
      context.user_data["admin_action"] = "send_file_to_user_upload"
      context.user_data["target_user"] = target_uid
      await update.message.reply_text("أرسل الملف الآن (أي نوع ملف)." + SIGNATURE)
      return
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
      await update.message.reply_text(f"Broadcast complete. Sent: {sent}, Failed: {failed}" + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      context.user_data.pop("admin_action", None)
      return
  if action == "add_balance":
      try:
          parts = text.split()
          target_uid, amount = parts[0], float(parts[1])
          data = load_data()
          data.setdefault("balances", {})[target_uid] = data.get("balances", {}).get(target_uid, 0) + amount
          save_data(data)
          await update.message.reply_text(f"✅ Added ${amount} to user {target_uid}. Balance: ${data['balances'][target_uid]}" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          context.user_data.pop("admin_action", None)
      except Exception:
          await update.message.reply_text("❌ Wrong format: user_id amount" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if action == "withdraw":
      try:
          parts = text.split()
          target_uid, amount = parts[0], float(parts[1])
          data = load_data()
          if data.get("balances", {}).get(target_uid, 0) < amount:
              await update.message.reply_text(f"❌ Insufficient balance! Available: ${data.get('balances', {}).get(target_uid, 0)}" + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
          else:
              data["balances"][target_uid] -= amount
              save_data(data)
              await update.message.reply_text(f"✅ Withdrawn ${amount} from {target_uid}. Balance: ${data['balances'][target_uid]}" + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
              context.user_data.pop("admin_action", None)
      except Exception:
          await update.message.reply_text("❌ Wrong format: user_id amount" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_menu")]]))
      return
  if action == "add_keys":
      product = context.user_data.get("add_keys_product")
      duration = context.user_data.get("add_keys_duration")
      if not product or not duration:
          await update.message.reply_text("❌ يجب اختيار المنتج والمدة أولاً من لوحة الأدمن." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_add_keys")]]))
          return
      keys = [k.strip() for k in text.split("\n") if k.strip()]
      if not keys:
          await update.message.reply_text("❌ لم يتم إدخال أي مفاتيح." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=f"admin_add_keys_duration:{product}:{duration}")]]))
          return
      data = load_data()
      key_name = f"{product}_{duration}"
      data.setdefault("keys", {}).setdefault(key_name, []).extend(keys)
      save_data(data)
      await update.message.reply_text(f"✅ تم إضافة {len(keys)} مفتاح لـ {product} ({duration}يوم)." + SIGNATURE,
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=f"admin_add_keys_product:{product}")]]))
      context.user_data.clear()
      return
  if action == "add_seller_balance":
      try:
          sid = context.user_data.get("target_seller")
          amount = float(text)
          data = load_data()
          if sid not in data.get("sellers", {}):
              await update.message.reply_text("❌ Seller not found!" + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
          else:
              data["sellers"][sid]["balance"] = data["sellers"][sid].get("balance", 0) + amount
              save_data(data)
              await update.message.reply_text(f"✅ Added ${amount} to seller {sid}. New balance: ${data['sellers'][sid]['balance']}" + SIGNATURE,
                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      except Exception:
          await update.message.reply_text("❌ Wrong format: amount" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      context.user_data.pop("admin_action", None)
      context.user_data.pop("target_seller", None)
      return
  if action == "create_key":
      product = context.user_data.get("create_key_product")
      duration = context.user_data.get("create_key_duration")
      key = text.strip()
      data = load_data()
      key_name = key_storage_name(product, duration)
      data.setdefault("keys", {}).setdefault(key_name, []).append(key)
      save_data(data)
      await update.message.reply_text(
          f"✅ تم إنشاء الكيز لـ {product} ({duration}يوم)!\n\nها هو الكيز:\n`{key}`" + SIGNATURE,
          parse_mode="Markdown",
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="admin_create_key_product:"+product)]])
      )
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
          if seller_id == "global":
              prices.setdefault("global", {}).setdefault(product, {})[duration] = price_val
          else:
              prices.setdefault("sellers", {}).setdefault(seller_id, {}).setdefault(product, {})[duration] = price_val
          save_prices(prices)
          await update.message.reply_text(
              f"✅ تم تعديل السعر: {product} ({duration}يوم) - السعر الجديد لـ {'GLOBAL' if seller_id == 'global' else seller_id}: ${price_val}" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data=f"edit_price:{product}")]])
          )
      except Exception:
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
          data.setdefault("sellers", {})[sid] = {"name": name, "balance": 0, "sales_count": 0}
          save_data(data)
          await update.message.reply_text(f"✅ Seller '{name}' (ID: {sid}) added." + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
          context.user_data.pop("admin_action", None)
      except Exception:
          await update.message.reply_text("❌ Wrong format: seller_id name" + SIGNATURE,
              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="admin_sellers")]]))
      return
  if action == "remove_seller":
      data = load_data()
      sid = text.strip()
      if sid in data.get("sellers", {}):
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

  if text == button_texts["activity"][lang]:
      DATA_STAT = load_data()
      uid = str(update.message.from_user.id)
      admins = set(DATA_STAT.get("admins", []))
      sellers_map = DATA_STAT.get("sellers", {})
      is_seller = uid in sellers_map or (uid.isdigit() and int(uid) in sellers_map)
      if is_seller:
          seller = sellers_map.get(uid, {}) if uid in sellers_map else sellers_map.get(int(uid), {})
          balance = seller.get("balance", 0)
          sales = [s for s in DATA_STAT.get("sales_log", []) if str(s.get("seller_id")) == str(uid)]
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
      if uid in admins:
          msg = build_customer_activity_message(DATA_STAT, uid, update.message.from_user.username)
          await update.message.reply_text(msg + SIGNATURE)
          return
      msg = build_customer_activity_message(DATA_STAT, uid, update.message.from_user.username)
      await update.message.reply_text(msg + SIGNATURE)
      return

  if text == button_texts["buy"][lang]:
      PRICES = load_prices()
      product_names = {
          "FREE": {"en": "🔮 FREE FIRE", "ar": "🔮 فري فاير", "fr": "🔮 FREE FIRE", "es": "🔮 FREE FIRE", "de": "🔮 FREE FIRE", "tr": "🔮 FREE FIRE"},
          "WIZARD": {"en": "✨ WIZARD", "ar": "✨ ويزارد", "fr": "✨ WIZARD", "es": "✨ WIZARD", "de": "✨ WIZARD", "tr": "✨ WIZARD"},
          "BUY_CERT": {"en": "🎖️ BUY CERT", "ar": "🎖️ شراء شهادة", "fr": "🎖️ BUY CERT", "es": "🎖️ BUY CERT", "de": "🎖️ BUY CERT", "tr": "🎖️ BUY CERT"},
          "CLOUD": {"en": "☁️ CLOUD", "ar": "☁️ كلاود", "fr": "☁️ CLOUD", "es": "☁️ CLOUD", "de": "☁️ CLOUD", "tr": "☁️ CLOUD"},
          "CODM_IOS": {"en": "📱 CODM IOS", "ar": "📱 كودم IOS", "fr": "📱 CODM IOS", "es": "📱 CODM IOS", "de": "📱 CODM IOS", "tr": "📱 CODM IOS"},
          "TERMINAL_X_PC": {"en": "💻 TERMINAL X PC", "ar": "💻 تيرمنال X PC", "fr": "💻 TERMINAL X PC", "es": "💻 TERMINAL X PC", "de": "💻 TERMINAL X PC", "tr": "💻 TERMINAL X PC"},
          "HG_CHEATS_ROOT": {"en": "🛡️ HG CHEATS ROOT", "ar": "🛡️ HG شيتس روت", "fr": "🛡️ HG CHEATS ROOT", "es": "🛡️ HG CHEATS ROOT", "de": "🛡️ HG CHEATS ROOT", "tr": "🛡️ HG CHEATS ROOT"}
      }
      products = list(product_names.keys())
      buttons = [product_names[p][lang] for p in products]
      reply_keyboard = build_rows(buttons, 2)
      DATA_CHECK = load_data()
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

  if text == button_texts["balance"][lang]:
      user_id = str(update.message.from_user.id)
      data = load_data()
      bal = data.get("balances", {}).get(user_id, 0)
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


def main():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Set your TELEGRAM_BOT_TOKEN in the code!")
        return
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler((filters.TEXT | filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.VOICE | filters.ANIMATION) & ~filters.COMMAND, message_handler))
    print("Bot running...")
    try:
        app.run_polling(drop_pending_updates=True)
    except telegram.error.Conflict as e:
        print("Failed to start bot: another getUpdates poller is active for this token.")
        print("telegram.error.Conflict:", e)
        return
    except Exception as e:
        print("Failed to start bot:", e)
        return


if __name__ == "__main__":
    try:
        from flask import Flask
        from threading import Thread
        import os

        # Keep-alive server for deployment platforms
        app = Flask('')

        @app.route('/')
        def home():
            return "Bot is alive!"

        def run():
            port = int(os.environ.get("PORT", 8080))
            app.run(host='0.0.0.0', port=port)

        keep_alive_thread = Thread(target=run)
        keep_alive_thread.daemon = True
        keep_alive_thread.start()
    except ImportError:
        print("Flask not installed, skipping keep-alive server.")
    
    main()


