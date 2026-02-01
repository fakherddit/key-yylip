"""
ملف حفظ البيانات الاحتياطية - Backup and Debug File
يحافظ على بيانات البوت عند التحديث ويساعد في استعادتها
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
import sys
import io

# تعيين UTF-8 للإخراج
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# الإعدادات
DB_PATH = os.getenv("DB_PATH", "bot.db")
BACKUP_PATH = "backup_bot.db"
BACKUP_JSON_PATH = "backup_data.json"
LOG_FILE = "bot_data_log.txt"

def log_message(message):
    """تسجيل الرسائل في ملف السجل"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text = f"[{timestamp}] {message}\n"
    print(log_text.strip())
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_text)
    except Exception as e:
        print(f"خطأ في تسجيل السجل: {e}")

def backup_database():
    """عمل نسخة احتياطية من قاعدة البيانات"""
    try:
        if os.path.exists(DB_PATH):
            shutil.copy(DB_PATH, BACKUP_PATH)
            log_message(f"✅ تم عمل نسخة احتياطية من قاعدة البيانات: {BACKUP_PATH}")
            return True
        else:
            log_message(f"⚠️  قاعدة البيانات غير موجودة: {DB_PATH}")
            return False
    except Exception as e:
        log_message(f"❌ خطأ في عمل النسخة الاحتياطية: {e}")
        return False

def export_data_to_json():
    """تصدير جميع البيانات إلى ملف JSON"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        data = {}
        
        # استخراج البيانات من جميع الجداول
        tables = ['users', 'sellers', 'keys', 'prices', 'sales_log', 'stats']
        
        for table in tables:
            try:
                cur.execute(f'SELECT * FROM {table}')
                rows = cur.fetchall()
                data[table] = [dict(row) for row in rows]
                log_message(f"✅ تم تصدير {len(rows)} صف من جدول {table}")
            except Exception as e:
                log_message(f"⚠️  لم يتم العثور على جدول {table}: {e}")
                data[table] = []
        
        # حفظ البيانات في JSON
        with open(BACKUP_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=str)
        
        log_message(f"✅ تم تصدير جميع البيانات إلى: {BACKUP_JSON_PATH}")
        return data
        
    except Exception as e:
        log_message(f"❌ خطأ في تصدير البيانات: {e}")
        return None
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def restore_database():
    """استعادة قاعدة البيانات من النسخة الاحتياطية"""
    try:
        if os.path.exists(BACKUP_PATH):
            shutil.copy(BACKUP_PATH, DB_PATH)
            log_message(f"✅ تم استعادة قاعدة البيانات من النسخة الاحتياطية")
            return True
        else:
            log_message(f"⚠️  لا توجد نسخة احتياطية لاستعادتها: {BACKUP_PATH}")
            return False
    except Exception as e:
        log_message(f"❌ خطأ في استعادة قاعدة البيانات: {e}")
        return False

def get_all_data():
    """الحصول على ملخص جميع البيانات المهمة"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "users_count": 0,
            "sellers_count": 0,
            "keys_count": 0,
            "used_keys_count": 0,
            "total_sales": 0,
            "stats": {}
        }
        
        # عد الجداول المختلفة
        cur.execute('SELECT COUNT(*) as count FROM users')
        summary["users_count"] = cur.fetchone()['count']
        
        cur.execute('SELECT COUNT(*) as count FROM sellers')
        summary["sellers_count"] = cur.fetchone()['count']
        
        cur.execute('SELECT COUNT(*) as count FROM keys')
        summary["keys_count"] = cur.fetchone()['count']
        
        cur.execute('SELECT COUNT(*) as count FROM keys WHERE is_used = 1')
        summary["used_keys_count"] = cur.fetchone()['count']
        
        cur.execute('SELECT COUNT(*) as count FROM sales_log')
        summary["total_sales"] = cur.fetchone()['count']
        
        cur.execute('SELECT * FROM stats')
        stats = cur.fetchall()
        if stats:
            summary["stats"] = dict(stats[0])
        
        cur.close()
        conn.close()
        
        return summary
        
    except Exception as e:
        log_message(f"❌ خطأ في الحصول على البيانات: {e}")
        return None

def print_data_status():
    """طباعة حالة البيانات الحالية"""
    summary = get_all_data()
    if summary:
        log_message("=" * 50)
        log_message("📊 ملخص البيانات الحالية:")
        log_message(f"👥 عدد المستخدمين: {summary['users_count']}")
        log_message(f"🏪 عدد البائعين: {summary['sellers_count']}")
        log_message(f"🔑 عدد المفاتيح الكلي: {summary['keys_count']}")
        log_message(f"✅ عدد المفاتيح المستخدمة: {summary['used_keys_count']}")
        log_message(f"💰 عدد المبيعات: {summary['total_sales']}")
        log_message("=" * 50)

def initialize_backup_system():
    """بدء نظام النسخ الاحتياطية"""
    log_message("🚀 بدء نظام حفظ البيانات...")
    log_message(f"📁 مسار قاعدة البيانات: {DB_PATH}")
    log_message(f"💾 مسار النسخة الاحتياطية: {BACKUP_PATH}")
    log_message(f"📄 مسار ملف JSON: {BACKUP_JSON_PATH}")
    
    # إنشاء النسخة الاحتياطية
    backup_database()
    
    # تصدير البيانات إلى JSON
    export_data_to_json()
    
    # طباعة حالة البيانات
    print_data_status()
    
    log_message("✅ تم تهيئة نظام حفظ البيانات بنجاح!")

if __name__ == "__main__":
    initialize_backup_system()
