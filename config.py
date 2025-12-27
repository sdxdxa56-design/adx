"""
config.py - إعدادات المنصة وأمان المفاتيح
"""

import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

class Config:
    # إعدادات الجلسة
    SESSION_TIMEOUT = 3600  # ثانية
    MAX_REQUESTS_PER_USER = 5
    ADMIN_USERS = ["admin@adx.com", "developer@adx.com"]
    
    # مسارات الملفات
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
    
    # إعدادات قاعدة البيانات
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///adx_platform.db")
    
    # مفاتيح API (يتم تحميلها من متغيرات البيئة)
    API_KEYS = {
        "groq": os.getenv("GROQ_API_KEY"),
        "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        "gemini": os.getenv("GEMINI_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY")
    }
    
    # إعدادات FAISS
    FAISS_INDEX_PATH = os.path.join(DATA_DIR, "indexed", "faiss.index")
    FAISS_METADATA_PATH = os.path.join(DATA_DIR, "indexed", "metadata.json")
    
    # مؤسسات دولية معتمدة
    INTERNATIONAL_INSTITUTIONS = {
        "UN": {
            "name": "الأمم المتحدة",
            "description": "منظمة دولية تهني بالسلام والأمن الدولي",
            "icon": "UN.svg",
            "legal_domain": ["حقوق الإنسان", "القانون الدولي", "السلام والأمن"]
        },
        "ICC": {
            "name": "المحكمة الجنائية الدولية",
            "description": "محكمة دولية دائمة لمحاكمة مرتكبي الجرائم الدولية",
            "icon": "ICC.svg",
            "legal_domain": ["جرائم حرب", "جرائم ضد الإنسانية", "إبادة جماعية"]
        },
        "WTO": {
            "name": "منظمة التجارة العالمية",
            "description": "منظمة دولية تشرف على قواعد التجارة بين الأمم",
            "icon": "WTO.svg",
            "legal_domain": ["قانون تجاري دولي", "منازعات تجارية", "اتفاقيات تجارية"]
        },
        "WHO": {
            "name": "منظمة الصحة العالمية",
            "description": "وكالة متخصصة تابعة للأمم المتحدة معنية بالصحة العامة",
            "icon": "WHO.svg",
            "legal_domain": ["قانون صحي دولي", "لوائح صحية", "أوبئة"]
        },
        "EU": {
            "name": "الاتحاد الأوروبي",
            "description": "اتحاد سياسي واقتصادي لدول أوروبية",
            "icon": "EU.svg",
            "legal_domain": ["قانون الاتحاد الأوروبي", "تشريعات أوروبية"]
        }
    }
    
    # دول مع دعم خاص
    SUPPORTED_COUNTRIES = {
        "Yemen": {"legal_system": "مدني وإسلامي", "language": "العربية"},
        "Saudi Arabia": {"legal_system": "إسلامي", "language": "العربية"},
        "Egypt": {"legal_system": "مدني", "language": "العربية"},
        "United Arab Emirates": {"legal_system": "مدني وإسلامي", "language": "العربية"},
        "Qatar": {"legal_system": "مدني وإسلامي", "language": "العربية"},
        "Jordan": {"legal_system": "مدني", "language": "العربية"},
        "Kuwait": {"legal_system": "مدني وإسلامي", "language": "العربية"},
        "Oman": {"legal_system": "مدني وإسلامي", "language": "العربية"}
    }

# إنشاء مجلدات إذا لم تكن موجودة
os.makedirs(Config.DATA_DIR, exist_ok=True)
os.makedirs(Config.ICONS_DIR, exist_ok=True)
os.makedirs(os.path.join(Config.DATA_DIR, "indexed"), exist_ok=True)