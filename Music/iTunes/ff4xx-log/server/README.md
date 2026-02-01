# ST FAMILY License Key Server Setup

## Files Included:
1. **validate.php** - Key validation endpoint
2. **generate.php** - Key generation endpoint
3. **database.sql** - Database schema

## Setup Instructions:

### 1. Database Setup
```bash
# Login to MySQL
mysql -u root -p

# Run the database script
mysql -u root -p < database.sql
```

### 2. Configure PHP Files
Edit both `validate.php` and `generate.php`:
```php
$servername = "localhost";
$username = "your_db_user";      // Change this
$password = "your_db_password";  // Change this
$dbname = "license_keys";
```

### 3. Upload to Server
Upload all files to your web server:
```
/var/www/html/license/
├── validate.php
├── generate.php
└── database.sql
```

### 4. Update Tweak Configuration
In `savagexiter.mm`, update the server URL:
```objc
static NSString* serverURL = @"https://your-domain.com/license/validate.php";
```

### 5. Set Permissions
```bash
chmod 644 validate.php generate.php
chmod 600 database.sql
```

## API Endpoints:

### Validate Key
**POST** `https://your-domain.com/license/validate.php`
```json
{
  "key": "XXXX-XXXX-XXXX-XXXX",
  "hwid": "device-hwid"
}
```

Response:
```json
{
  "valid": true,
  "message": "Key activated successfully!",
  "expiry_date": "2026-02-28 23:59:59"
}
```

### Generate Keys
**GET** `https://your-domain.com/license/generate.php?count=10&days=30`

Response:
```json
{
  "success": true,
  "message": "10 keys generated",
  "keys": [
    {
      "key": "A1B2-C3D4-E5F6-G7H8",
      "expiry_date": "2026-02-28 23:59:59"
    }
  ]
}
```

## Security Notes:
- Change default admin password in database.sql
- Use HTTPS for all connections
- Keep database credentials secure
- Regularly backup the database
- Add rate limiting to prevent abuse
- Consider adding IP whitelisting

## Testing:
```bash
# Generate a test key
curl "https://your-domain.com/license/generate.php?count=1&days=30"

# Validate the key
curl -X POST https://your-domain.com/license/validate.php \
  -H "Content-Type: application/json" \
  -d '{"key":"XXXX-XXXX-XXXX-XXXX","hwid":"test-device"}'
```

## Troubleshooting:
- If validation fails, check server logs: `/var/log/apache2/error.log`
- Verify database connection settings
- Ensure PHP has mysqli extension enabled
- Check file permissions
