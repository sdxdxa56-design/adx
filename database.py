"""
database.py - إدارة قاعدة البيانات
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class Database:
    """فئة لإدارة قاعدة البيانات"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_URL.replace("sqlite:///", "")
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            country TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            total_requests INTEGER DEFAULT 0,
            quota_used INTEGER DEFAULT 0,
            is_banned BOOLEAN DEFAULT FALSE,
            metadata TEXT
        )
        ''')
        
        # جدول الطلبات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            country TEXT,
            issue_length INTEGER,
            institutions TEXT,
            analysis_model TEXT,
            response_time REAL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        # جدول السجلات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level TEXT,
            message TEXT,
            details TEXT
        )
        ''')
        
        # جدول الإعدادات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_usage(self, user_id: str, country: str, 
                    issue_length: int, institutions: List[str]):
        """تسجيل استخدام جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود المستخدم
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, country, first_seen, last_seen)
        VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (user_id, country))
        
        # تحديث آخر ظهور
        cursor.execute('''
        UPDATE users 
        SET last_seen = CURRENT_TIMESTAMP,
            total_requests = total_requests + 1,
            quota_used = quota_used + 1
        WHERE user_id = ?
        ''', (user_id,))
        
        # تسجيل الطلب
        cursor.execute('''
        INSERT INTO requests (user_id, country, issue_length, institutions)
        VALUES (?, ?, ?, ?)
        ''', (user_id, country, issue_length, json.dumps(institutions)))
        
        conn.commit()
        conn.close()
    
    def get_user_quota(self, user_id: str) -> int:
        """الحصول على الحصة المتبقية للمستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT quota_used FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            used = result[0]
            return max(0, Config.MAX_REQUESTS_PER_USER - used)
        
        return Config.MAX_REQUESTS_PER_USER
    
    def get_total_users(self) -> int:
        """إجمالي عدد المستخدمين"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        result = cursor.fetchone()[0]
        conn.close()
        
        return result
    
    def get_total_requests(self) -> int:
        """إجمالي عدد الطلبات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM requests')
        result = cursor.fetchone()[0]
        conn.close()
        
        return result
    
    def get_today_requests(self) -> int:
        """طلبات اليوم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) FROM requests 
        WHERE DATE(timestamp) = DATE('now')
        ''')
        
        result = cursor.fetchone()[0]
        conn.close()
        
        return result
    
    def get_popular_countries(self) -> List[tuple]:
        """الدول الأكثر استخداماً"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT country, COUNT(*) as count 
        FROM requests 
        GROUP BY country 
        ORDER BY count DESC 
        LIMIT 10
        ''')
        
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_weekly_usage(self) -> List[tuple]:
        """الاستخدام الأسبوعي"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT DATE(timestamp) as day, COUNT(*) as count
        FROM requests 
        WHERE timestamp >= DATE('now', '-7 days')
        GROUP BY day
        ORDER BY day
        ''')
        
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_all_users(self, search: str = "") -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if search:
            cursor.execute('''
            SELECT * FROM users 
            WHERE user_id LIKE ? OR country LIKE ?
            ORDER BY last_seen DESC
            ''', (f"%{search}%", f"%{search}%"))
        else:
            cursor.execute('SELECT * FROM users ORDER BY last_seen DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def clean_old_data(self, days: int = 30) -> int:
        """تنظيف البيانات القديمة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # حذف الطلبات القديمة
        cursor.execute('''
        DELETE FROM requests 
        WHERE timestamp < DATE('now', ?)
        ''', (f"-{days} days",))
        
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def log_event(self, level: str, message: str, details: str = ""):
        """تسجيل حدث في السجلات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO logs (level, message, details)
        VALUES (?, ?, ?)
        ''', (level, message, details))
        
        conn.commit()
        conn.close()