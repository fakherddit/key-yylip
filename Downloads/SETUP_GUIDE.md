# ⚡ إعدادات سريعة للبوتات

## 🚀 الخطوة 1: احصل على التوكنات

### البوت الأول:
```
TOKEN_1 = "YOUR_FIRST_BOT_TOKEN"
```
> من @BotFather على تيليجرام

### البوت الثاني:
```
TOKEN_2 = "YOUR_SECOND_BOT_TOKEN"
```
> أنشئ بوت جديد من @BotFather

---

## 📝 الملفات المطلوبة:

### 1️⃣ `bot.py` (الأول)
- الإدارة الأساسية
- إضافة المفاتيح
- إدارة الأرصدة

### 2️⃣ `bot2.py` (الثاني)
- تغيير الأسعار (متقدم)
- تصميم البائعين

### 3️⃣ `requirements.txt`
```
python-telegram-bot==21.7
psycopg2-binary==2.9.10
httpx~=0.27
```

### 4️⃣ `.gitignore`
```
__pycache__/
*.py[cod]
*$py.class
.env
*.venv
```

---

## 🗄️ قاعدة البيانات:

```
DATABASE_URL=postgresql://pharm_db_qwum_user:ORxhLJpvjSumWLWQGDaqjQKEWUDeVFls@dpg-d5jp8vili9vc73bk3vcg-a.oregon-postgres.render.com/pharm_db_qwum
```

---

## 📦 النشر على Render:

### Bot 1:
- Web Service
- Start Command: `python bot.py`
- TOKEN من البيئة

### Bot 2:
- Web Service جديد
- Start Command: `python bot2.py`
- نفس DATABASE_URL

---

## 🎯 الاختبار المحلي:

```powershell
# اختبر البوت الأول
python bot.py

# في terminal جديد، اختبر البوت الثاني
python bot2.py
```

---

## ✅ التحقق:

كل بوت يجب أن يطبع:
```
Bot running...
```

---

## 📊 قاعدة البيانات المشتركة:

```
┌──────────────┐
│   Bot 1      │
└──────┬───────┘
       │
       ├──→ PostgreSQL ←──┐
       │                   │
       └───────────────────┤
                           │
                     ┌─────┴───────┐
                     │   Bot 2     │
                     └─────────────┘
```

---

## 🎨 مثال على التصميم:

### البائع A:
```json
{
  "color": "#FF5733",
  "welcome_message": "أهلاً في متجري!",
  "button_style": "premium",
  "logo_url": "https://example.com/logo.png"
}
```

### البائع B:
```json
{
  "color": "#00FF00",
  "welcome_message": "مرحباً بك!",
  "button_style": "modern",
  "logo_url": "https://example.com/logo2.png"
}
```

---

## 💰 مثال على الأسعار:

### السعر العام:
- FREE 1 day: $3

### سعر البائع A:
- FREE 1 day: $2.5 (أرخص)

### سعر البائع B:
- FREE 1 day: $3.5 (أغلى)

---

## 🔐 أكواد الإدمن:

```
ADMIN_CODE = "123123NNK"
```

---

Done! 🎉 الآن جاهز للعمل!
