"""
legal_advisor.py - المحرك الذكي للتحليل القانوني
"""

import random
import time
from typing import Dict, List, Optional
from groq import Groq
from openai import OpenAI
import google.generativeai as genai
from config import Config

class LegalAdvisor:
    """محامي ذكي متعدد المصادر مع نظام ترشيح ذكي"""
    
    def __init__(self):
        self.api_keys = Config.API_KEYS
        self.fallback_order = ["deepseek", "groq", "gemini", "openai"]
        self.request_history = []
        
    def _get_deepseek_response(self, prompt: str) -> Optional[str]:
        """استخدام DeepSeek API"""
        try:
            if not self.api_keys.get("deepseek"):
                return None
                
            client = OpenAI(
                api_key=self.api_keys["deepseek"],
                base_url="https://api.deepseek.com"
            )
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "أنت محامٍ دولي خبير بجميع القوانين المحلية والدولية. قدم إجابات دقيقة وعملية."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek Error: {e}")
            return None
    
    def _get_groq_response(self, prompt: str) -> Optional[str]:
        """استخدام Groq API"""
        try:
            if not self.api_keys.get("groq"):
                return None
                
            client = Groq(api_key=self.api_keys["groq"])
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "أنت مستشار قانوني ذكي. قدم حلولاً عملية وقابلة للتنفيذ."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}")
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
            
            return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None
    
    def _get_openai_response(self, prompt: str) -> Optional[str]:
        """استخدام OpenAI API"""
        try:
            if not self.api_keys.get("openai"):
                return None
                
            client = OpenAI(api_key=self.api_keys["openai"])
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "أنت محامٍ دولي متخصص في التحليل القانوني."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return None
    
    def get_intelligent_response(self, 
                                country: str, 
                                issue: str, 
                                institutions: List[str],
                                include_international: bool = True) -> Dict:
        """
        الحصول على رد ذكي باستخدام أفضل مصدر متاح
        
        Returns:
            Dict يحتوي على:
                - analysis: التحليل القانوني
                - suggested_solutions: الحلول المقترحة
                - steps: خطوات عملية
                - warnings: تحذيرات هامة
                - used_model: النموذج المستخدم
                - confidence: درجة الثقة
        """
        
        # بناء prompt ذكي
        institutions_text = ", ".join(institutions) if institutions else "لا توجد مؤسسات محددة"
        
        prompt = f"""
        دورك: محامٍ خبير في قوانين {country} والقانون الدولي.
        
        تفاصيل القضية:
        {issue}
        
        المؤسسات ذات الصلة: {institutions_text}
        تضمين قوانين دولية: {"نعم" if include_international else "لا"}
        
        المطلوب:
        1. **تحليل قانوني موجز** (نقاط رئيسية)
        2. **الحلول الممكنة** (مرتبة حسب الأفضلية)
        3. **خطوات عملية** (كيفية التقديم والإجراءات)
        4. **المستندات المطلوبة**
        5. **الجهات المختصة للتواصل**
        6. **التكاليف التقريبية والوقت المتوقع**
        7. **المخاطر والتحذيرات**
        8. **نصائح إضافية**
        
        قدم الإجابة بشكل منظم مع عناوين واضحة.
        """
        
        # محاولة المصادر بالترتيب الذكي
        response = None
        used_model = "none"
        
        for model_name in self.fallback_order:
            if response:
                break
                
            try:
                if model_name == "deepseek":
                    response = self._get_deepseek_response(prompt)
                    used_model = "DeepSeek"
                elif model_name == "groq":
                    response = self._get_groq_response(prompt)
                    used_model = "Groq (Llama)"
                elif model_name == "gemini":
                    response = self._get_gemini_response(prompt)
                    used_model = "Google Gemini"
                elif model_name == "openai":
                    response = self._get_openai_response(prompt)
                    used_model = "OpenAI GPT-4"
                    
                # انتظار قصير بين المحاولات
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error with {model_name}: {e}")
                continue
        
        # إذا فشلت جميع المصادر
        if not response:
            response = """
            ## ⚠️ تعذر الاتصال بخوادم التحليل
            
            **الحلول المؤقتة:**
            1. حاول تحديث الصفحة
            2. اختصر وصف المشكلة
            3. تواصل مع محامٍ مباشرة
            
            **للحصول على مساعدة فورية:**
            - اتصل بمركز المساعدة القانونية المحلي
            - استخدم خدمات الاستشارة المجانية
            - تواصل مع نقابة المحامين في دولتك
            
            **نحن نعمل على حل المشكلة...**
            """
            used_model = "Fallback"
        
        # تحليل الاستجابة وتنظيمها
        return self._structure_response(response, used_model)
    
    def _structure_response(self, raw_response: str, used_model: str) -> Dict:
        """تنظيم الاستجابة إلى أقسام منظمة"""
        
        sections = {
            "analysis": "",
            "suggested_solutions": [],
            "steps": [],
            "documents": [],
            "authorities": [],
            "costs": "",
            "warnings": [],
            "additional_tips": [],
            "used_model": used_model,
            "confidence": random.uniform(0.7, 0.95)  # محاكاة لدرجة الثقة
        }
        
        # محاولة استخراج الأقسام من النص
        lines = raw_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "تحليل" in line or "Analysis" in line:
                current_section = "analysis"
            elif "حل" in line or "Solution" in line:
                current_section = "suggested_solutions"
            elif "خطوة" in line or "Step" in line:
                current_section = "steps"
            elif "مستند" in line or "Document" in line:
                current_section = "documents"
            elif "جهة" in line or "Authority" in line:
                current_section = "authorities"
            elif "تكلفة" in line or "Cost" in line:
                current_section = "costs"
            elif "تحذير" in line or "Warning" in line:
                current_section = "warnings"
            elif "نصيحة" in line or "Tip" in line:
                current_section = "additional_tips"
            
            elif current_section:
                if line and not line.startswith(("#", "##", "###")):
                    if current_section == "analysis":
                        sections["analysis"] += line + " "
                    elif current_section in ["suggested_solutions", "steps", "documents", 
                                           "authorities", "warnings", "additional_tips"]:
                        if line.startswith(("-", "•", "1.", "2.", "3.")):
                            sections[current_section].append(line)
        
        # إذا لم يتم استخراج الأقسام بشكل جيد
        if not sections["analysis"]:
            sections["analysis"] = raw_response[:500] + "..."
        
        return sections

# نسخة واحدة من المحامي
legal_advisor = LegalAdvisor()