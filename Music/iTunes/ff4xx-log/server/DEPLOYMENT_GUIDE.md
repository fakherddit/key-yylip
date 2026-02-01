# ST FAMILY - Render + Telegram Bot Deployment Guide

## 🚀 Complete Setup Guide

### Part 1: Render Deployment

#### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)

#### Step 2: Create PostgreSQL/MySQL Database
1. Click **"New +"** → **"PostgreSQL"** or use external MySQL
2. Name: `st-family-db`
3. Copy the **Internal Database URL**

#### Step 3: Deploy Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository or manual deploy
3. Configuration:
   - **Name**: `st-family-license`
   - **Runtime**: PHP
   - **Build Command**: `chmod +x render-build.sh && ./render-build.sh`
   - **Start Command**: `php -S 0.0.0.0:$PORT -t .`

#### Step 4: Environment Variables
Add these in Render dashboard:
```
DB_HOST=your-database-host
DB_USER=your-database-user
DB_PASS=your-database-password
DB_NAME=license_keys
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_ADMIN_ID=your-telegram-user-id
```

---

### Part 2: Telegram Bot Setup

#### Step 1: Create Bot
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Choose name: **ST FAMILY License Bot**
4. Choose username: `stfamily_license_bot`
5. Copy the **Bot Token**

#### Step 2: Get Your Telegram User ID
1. Message [@userinfobot](https://t.me/userinfobot)
2. Copy your **User ID** (numbers only)

#### Step 3: Set Webhook
Replace with your Render URL:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://st-family-license.onrender.com/telegram-webhook"
```

#### Step 4: Test Bot
1. Open your bot in Telegram
2. Send `/start`
3. You should see the main menu

---

### Part 3: Update Tweak Configuration

In `savagexiter.mm`, update the server URL:
```objc
static NSString* serverURL = @"https://st-family-license.onrender.com/validate";
```

Rebuild your tweak:
```bash
make clean package
```

---

### 📱 Bot Commands

**Admin Commands:**
- `/start` - Show main menu
- `/generate` - Generate license keys with buttons
- `/stats` - View database statistics
- `/list` - List last 20 active keys
- Send any key (e.g., `A1B2-C3D4-E5F6-G7H8`) to lookup details

**Generate Menu:**
- 1 Key - 7 Days
- 1 Key - 30 Days
- 5 Keys - 30 Days
- 10 Keys - 30 Days
- 1 Key - Lifetime
- 5 Keys - Lifetime

---

### 🔧 Manual Deployment (Without Git)

1. **Create folder structure:**
```
server/
├── index.php
├── validate.php
├── telegram_bot.php
├── generate_api.php
├── database.sql
├── render-build.sh
├── render.yaml
└── package.json
```

2. **Upload to Render:**
   - Zip all files
   - In Render dashboard: **Manual Deploy** → Upload ZIP

---

### 🧪 Testing

**Test Validation:**
```bash
curl -X POST https://st-family-license.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{"key":"TEST-1234-5678-90AB","hwid":"device-123"}'
```

**Test Health:**
```bash
curl https://st-family-license.onrender.com/health
```

---

### 📊 Monitoring

**Render Dashboard:**
- View logs in real-time
- Monitor API requests
- Track uptime

**Telegram:**
- Use `/stats` to see key usage
- Receive notifications (optional feature)

---

### 🔒 Security Checklist

✅ Database credentials in environment variables only  
✅ TELEGRAM_ADMIN_ID set to YOUR user ID only  
✅ Use HTTPS for all connections  
✅ Enable Render's DDoS protection  
✅ Regularly backup database  
✅ Monitor logs for suspicious activity  

---

### 🆘 Troubleshooting

**Bot not responding:**
```bash
# Check webhook status
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

**Database errors:**
- Verify environment variables in Render
- Check database.sql was executed
- Test database connection

**Validation failing:**
- Check Render logs for errors
- Verify server URL in tweak code
- Test with curl command above

---

### 💡 Advanced Features

**Add expiry notifications:**
Edit `telegram_bot.php` to send daily expiry alerts.

**Custom key formats:**
Modify key generation in `generate_api.php`.

**IP whitelisting:**
Add IP checks in `validate.php`.

---

### 📞 Support

For issues:
1. Check Render logs first
2. Test endpoints with curl
3. Verify bot webhook is active
4. Check database connection

---

## 🎉 You're Done!

Your license system is now live:
- ✅ Deployed on Render (free tier available)
- ✅ Telegram bot generates keys instantly
- ✅ HWID binding for security
- ✅ Real-time validation

**Next Steps:**
1. Generate your first keys via Telegram: `/generate`
2. Test in Free Fire with your tweak
3. Share keys with users
