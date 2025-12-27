"""
utils.py - أدوات مساعدة للمنصة
"""

import streamlit as st
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional

def generate_user_id() -> str:
    """إنشاء معرف فريد للمستخدم"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"user_{timestamp}_{random_str}"

def validate_input(text: str, min_length: int = 20) -> bool:
    """التحقق من صحة الإدخال"""
    if not text or len(text.strip()) < min_length:
        return False
    
    # التحقق من وجود كلمات مفيدة
    words = text.split()
    if len(words) < 5:
        return False
    
    return True

def format_arabic_text(text: str) -> str:
    """تنسيق النص العربي"""
    # إضافة علامات الترقيم إذا لم تكن موجودة
    if text and text[-1] not in ['.', '؟', '!']:
        text += '.'
    
    return text

def create_legal_template(template_type: str, **kwargs) -> str:
    """إنشاء قوالب قانونية"""
    
    templates = {
        "complaint": """
        السيد/ة رئيس {authority}
        
        الموضوع: شكوى ضد {party_name}
        
        أتقدم إليكم بهذه الشكوى بسبب {issue_summary}.
        
        التفاصيل:
        {details}
        
        المطلوب:
        {requests}
        
        المستندات المرفقة:
        {documents}
        
        وتفضلوا بقبول فائق الاحترام،
        {user_name}
        تاريخ: {date}
        """,
        
        "legal_advice_request": """
        إلى السادة المحامين/المستشارين القانونيين،
        
        أطلب مشورتكم القانونية في القضية التالية:
        
        نوع القضية: {case_type}
        الأطراف: {parties}
        التاريخ: {case_date}
        
        التفاصيل:
        {details}
        
        الأسئلة القانونية:
        {questions}
        
        وشكراً لتعاونكم،
        {user_name}
        """
    }
    
    if template_type in templates:
        template = templates[template_type]
        return template.format(**kwargs)
    
    return ""

def calculate_confidence_score(analysis_length: int, 
                             solution_count: int, 
                             has_warnings: bool) -> float:
    """حساب درجة الثقة في التحليل"""
    
    score = 0.0
    
    # طول التحليل
    if analysis_length > 500:
        score += 0.3
    elif analysis_length > 200:
        score += 0.2
    else:
        score += 0.1
    
    # عدد الحلول
    score += min(solution_count * 0.1, 0.3)
    
    # وجود تحذيرات (يدل على دقة)
    if has_warnings:
        score += 0.1
    
    # عامل عشوائي صغير
    score += random.uniform(0.0, 0.1)
    
    return min(score, 1.0)

def get_country_flag(country_name: str) -> str:
    """الحصول على علم الدولة"""
    
    flags = {
        "Yemen": "🇾🇪",
        "Saudi Arabia": "🇸🇦",
        "Egypt": "🇪🇬",
        "United Arab Emirates": "🇦🇪",
        "Qatar": "🇶🇦",
        "Jordan": "🇯🇴",
        "Kuwait": "🇰🇼",
        "Oman": "🇴🇲",
        "Bahrain": "🇧🇭",
        "Lebanon": "🇱🇧"
    }
    
    return flags.get(country_name, "🏳️")

def create_progress_steps(steps: List[str], current_step: int) -> str:
    """إنشاء خطوات التقدم"""
    
    html = '<div style="display: flex; justify-content: space-between; margin: 20px 0;">'
    
    for i, step in enumerate(steps):
        is_active = i == current_step
        is_completed = i < current_step
        
        html += f'''
        <div style="text-align: center; flex: 1;">
            <div style="width: 40px; height: 40px; border-radius: 50%; 
                       background: {'#4F46E5' if is_active else ('#10B981' if is_completed else '#E5E7EB')}; 
                       color: white; display: flex; align-items: center; justify-content: center; 
                       margin: 0 auto 10px; font-weight: bold;">
                {i + 1}
            </div>
            <span style="color: {'#4F46E5' if is_active else ('#6B7280' if not is_completed else '#10B981')}; 
                       font-size: 14px;">{step}</span>
        </div>
        '''
        
        if i < len(steps) - 1:
            html += f'''
            <div style="flex: 1; height: 2px; background: {'#4F46E5' if i < current_step else '#E5E7EB'}; 
                       margin-top: 20px;"></div>
            '''
    
    html += '</div>'
    
    return html

def format_time_ago(timestamp: datetime) -> str:
    """تنسيق الوقت المنقضي"""
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"قبل {years} سنة"
    elif diff.days > 30:
        months = diff.days // 30
        return f"قبل {months} شهر"
    elif diff.days > 0:
        return f"قبل {diff.days} يوم"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"قبل {hours} ساعة"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"قبل {minutes} دقيقة"
    else:
        return "الآن"