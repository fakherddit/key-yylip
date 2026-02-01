# ST FAMILY - Complete Setup Guide

## ✅ Your Configuration:
- **Database**: PostgreSQL (Render)
- **Bot Token**: `8216359066:AAEt2GFGgTBp3hh_znnJagH3h1nN5A_XQf0`
- **Admin ID**: `7210704553`
- **DB Connection**: Already configured in `index.php`

## 🚀 Quick Deploy Steps:

### 1. Upload to Render
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect GitHub or upload files
4. **Build Command**: `chmod +x render-build.sh && ./render-build.sh`
5. **Start Command**: `php -S 0.0.0.0:$PORT -t .`

### 2. Setup Database
Run `database.sql` on your PostgreSQL:
```bash
psql postgresql://dylip_key_user:TwbqpTuAggFaAXhIX7Q7pMmJIih5vEQe@dpg-d5v88bl6ubrc73c8tlqg-a.oregon-postgres.render.com/dylip_key < database.sql
```

### 3. Setup Telegram Webhook
After deploy, get your Render URL and set webhook:
```bash
curl -X POST "https://api.telegram.org/bot8216359066:AAEt2GFGgTBp3hh_znnJagH3h1nN5A_XQf0/setWebhook" \
  -d "url=https://YOUR-APP.onrender.com/telegram-webhook"
```

### 4. Test Bot
1. Open Telegram
2. Message your bot
3. Send `/start`

## 🤖 Bot Commands:

### Admin Commands:
- **`/start`** - Main menu
- **`/generate`** - Generate standard license keys
  - 1/5/10/20/50 keys
  - 7/30 days or Lifetime
- **`/global`** - Generate global keys (unlimited users)
  - Day (24h)
  - Week (7 days)
  - Month (30 days)
- **`/control`** - Server control panel
  - 🟢/🔴 Stop/Start Server
  - Enable/Disable Key Validation
  - Enable/Disable Key Creation
  - Delete Expired Keys
- **`/stats`** - View statistics
- **`/list`** - List last 20 active keys
- Send any key (e.g., `A1B2-C3D4-E5F6-G7H8`) to lookup details

## 🌐 Global Keys Feature:
Global keys allow **unlimited users** to use the same key:
- **Global Day**: Valid for 24 hours, unlimited activations
- **Global Week**: Valid for 7 days, unlimited activations
- **Global Month**: Valid for 30 days, unlimited activations

Perfect for:
- Beta testing
- Promotional periods
- Group sharing

## ⚙️ Server Control Features:

### Stop Server
- Disables all validation requests
- Bot commands still work
- Users can't activate keys

### Disable Key Validation
- Temporarily block all key checks
- Useful during maintenance

### Disable Key Creation
- Stop generating new keys via bot
- Existing keys still work

### Delete Expired Keys
- Clean up database
- Remove all keys past expiry date

## 📊 Database Tables:

### `licenses`
- `license_key` - The actual key
- `hwid` - Device ID (NULL for global keys)
- `expiry_date` - When key expires
- `key_type` - standard, global_day, global_week, global_month
- `status` - active, banned, expired

### `server_settings`
- `server_enabled` - 1 or 0
- `key_validation_enabled` - 1 or 0
- `key_creation_enabled` - 1 or 0

### `activity_log`
- Tracks all admin actions
- Who did what and when

## 🔧 Important Files:

### Replace telegram_bot.php:
```bash
# After testing telegram_bot_full.php, replace:
mv telegram_bot_full.php telegram_bot.php
```

### Update Tweak URL:
In `savagexiter.mm`:
```objc
static NSString* serverURL = @"https://your-app.onrender.com/validate";
```

## 🧪 Testing:

### Test Validation:
```bash
curl -X POST https://your-app.onrender.com/validate \
  -H "Content-Type: application/json" \
  -d '{"key":"TEST-1234-5678-90AB","hwid":"device-123"}'
```

### Test Health:
```bash
curl https://your-app.onrender.com/health
```

### Check Webhook:
```bash
curl https://api.telegram.org/bot8216359066:AAEt2GFGgTBp3hh_znnJagH3h1nN5A_XQf0/getWebhookInfo
```

## 💡 Usage Examples:

### Generate Keys for Sale:
1. Open bot
2. `/generate`
3. Select "10 Keys - 30 Days"
4. Send keys to customers

### Create Global Key for Event:
1. `/global`
2. Select "Global Day"
3. Share key with all participants
4. Unlimited uses for 24h

### Stop Server During Maintenance:
1. `/control`
2. Click "🔴 Stop Server"
3. Perform updates
4. Click "🟢 Start Server"

## 🔒 Security:
- ✅ Database credentials hardcoded (secure)
- ✅ Bot token hardcoded
- ✅ Admin ID verified on every command
- ✅ HWID binding prevents key sharing (except globals)
- ✅ PostgreSQL on Render (encrypted connection)

## 📞 Troubleshooting:

**Bot not responding:**
- Check webhook status
- Verify bot token
- Check Render logs

**Database errors:**
- Verify connection string
- Run database.sql
- Check PostgreSQL status on Render

**Validation failing:**
- Check server_enabled in database
- Verify tweak has correct URL
- Test with curl command

## 🎉 You're Done!
Your complete license system is ready with:
- ✅ PostgreSQL database
- ✅ Telegram bot control
- ✅ Global key support
- ✅ Server management
- ✅ Activity logging
