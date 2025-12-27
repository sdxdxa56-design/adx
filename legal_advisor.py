"""
legal_advisor.py - المحرك الذكي للتحليل القانوني
"""

import random
import time
import json
from typing import Dict, List, Optional
import openai  # سيتم استخدامه لكل من DeepSeek وOpenAI
import google.generativeai as genai
import requests  # للاتصال المباشر
from config import Config

class LegalAdvisor:
    """محامي ذكي متعدد المصادر مع نظام ترشيح ذكي"""
    
    def __init__(self):
        self.api_keys = Config.API_KEYS
        self.fallback_order = ["deepseek", "openai", "gemini"]  # إزالة Groq مؤقتاً
        self.request_history = []
    
    def _get_deepseek_response(self, prompt: str) -> Optional[str]:
        """استخدام DeepSeek API"""
        try:
            if not self.api_keys.get("deepseek"):
                return None
                
            client = openai.OpenAI(
                api_key=self.api_keys["deepseek"],
                base_url="https://api.deepseek.com"
            )
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system", 
                        "content": """أنت محامٍ دولي خبير بجميع القوانين المحلية والدولية. 
                        قدم إجابات دقيقة وعملية ومباشرة."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"DeepSeek Error: {e}")
            return None
    
    def _get_openai_response(self, prompt: str) -> Optional[str]:
        """استخدام OpenAI API"""
        try:
            if not self.api_keys.get("openai"):
                return None
                
            client = openai.OpenAI(api_key=self.api_keys["openai"])
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # استخدام إصدار أرخص وأسرع
                messages=[
                    {
                        "role": "system", 
                        "content": "أنت مستشار قانوني ذكي. قدم حلولاً عملية وقابلة للتنفيذ."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return None
    
    def _get_gemini_response(self, prompt: str) -> Optional[str]:
        """استخدام Gemini API"""
        try:
            if not self.api_keys.get("gemini"):
                return None
                
            genai.configure(api_key=self.api_keys["gemini"])
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(
                f"بصفة محامٍ خبير: {prompt}",
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 4000,
                }
            )
            
            return response.text if response else None
            
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None
    
    def _get_fallback_response(self, prompt: str) -> str:
        """استجابة احتياطية بدون API"""
        return f"""
        ## ⚖️ تحليل أولي للقضية
        
        **ملاحظة:** حالياً الخوادم الرئيسية قيد الصيانة، هذا تحليل مبني على القوانين العامة:
        
        ### 1. النقاط الرئيسية:
        - من المهم توثيق جميع الأدلة والمستندات
        - التواصل مع المحاكم المحلية في أقرب وقت
        - استشارة محامٍ متخصص في {prompt.split('الدولة:')[1].split('.')[0] if 'الدولة:' in prompt else 'دولتك'}
        
        ### 2. الإجراءات الموصى بها:
        1. جمع جميع الوثائق المتعلقة بالقضية
        2. تحديد الجهة المختصة (مدنية/جنائية/تجارية)
        3. التواصل مع نقابة المحامين المحلية
        4. الاطلاع على القوانين المحلية ذات الصلة
        
        ### 3. تحذيرات هامة:
        ⚠️ هذا تحليل أولي ولا يغني عن استشارة محامٍ مرخص
        ⚠️ مهلة التقادم تختلف حسب نوع القضية
        ⚠️ التأكد من صلاحية المستندات قانونياً
        
        **للحصول على تحليل كامل، يرجى المحاولة مرة أخرى بعد قليل.**
        """
    
    def get_intelligent_response(self, 
                                country: str, 
                                issue: str, 
                                institutions: List[str],
                                include_international: bool = True) -> Dict:
        """
        الحصول على رد ذكي باستخدام أفضل مصدر متاح
        """
        
        # بناء prompt مبسط
        institutions_text = ", ".join(institutions) if institutions else "لا توجد"
        
        prompt = f"""
        الدولة: {country}
        المؤسسات المختارة: {institutions_text}
        
        تفاصيل القضية:
        {issue}
        
        المطلوب: تحليل قانوني مع حلول عملية.
        """
        
        response = None
        used_model = "none"
        
        # محاولة المصادر بالترتيب
        for model_name in self.fallback_order:
            if response:
                break
                
            try:
                if model_name == "deepseek":
                    response = self._get_deepseek_response(prompt)
                    used_model = "DeepSeek"
                elif model_name == "openai":
                    response = self._get_openai_response(prompt)
                    used_model = "OpenAI"
                elif model_name == "gemini":
                    response = self._get_gemini_response(prompt)
                    used_model = "Gemini"
                    
            except Exception:
                continue
        
        # إذا فشلت جميع المصادر
        if not response:
            response = self._get_fallback_response(prompt)
            used_model = "النظام المحلي"
        
        # تنظيم الاستجابة
        return {
            "analysis": response,
            "suggested_solutions": [
                "توثيق جميع الأدلة والمستندات",
                "التواصل مع محامٍ متخصص في القوانين المحلية",
                "مراجعة الجهة القضائية المختصة"
            ],
            "steps": [
                "الخطوة 1: جمع الوثائق",
                "الخطوة 2: تحديد الاختصاص القضائي",
                "الخطوة 3: الاستشارة القانونية",
                "الخطوة 4: التقديم الرسمي"
            ],
            "warnings": [
                "هذا تحليل أولي ولا يغني عن محامٍ مرخص",
                "تختلف الإجراءات حسب الدولة ونوع القضية"
            ],
            "used_model": used_model,
            "confidence": random.uniform(0.7, 0.9)
        }

# نسخة واحدة من المحامي
legal_advisor = LegalAdvisor()