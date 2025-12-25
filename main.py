import streamlit as st
from groq import Groq
from openai import OpenAI
import google.generativeai as genai
import pycountry
import os
from streamlit.components.v1 import html as components_html

# --- 1. إعداد قائمة المفاتيح والشركات ---
# ملاحظة: تم وضع المفاتيح التي أرسلتها هنا
GROQ_KEYS = ["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"]
DEEPSEEK_KEY = "sk-c0f41687f834493a92291dba703f96ad"
GEMINI_KEY = "AIzaSyAmo52YQe2oAReIInKt-LaPTA9PVB6eh7Q"
OPENAI_KEY = "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"

# --- 2. نظام إدارة الحصص (5 محاولات لكل زائر) ---
if 'user_usage' not in st.session_state:
    st.session_state['user_usage'] = 0

MAX_FREE_LIMIT = 5

# --- 3. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="منصة adx | المُحكم الرقمي", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .report-card { background-color: #f8fafc; padding: 20px; border-radius: 10px; border-right: 6px solid #0f766e; color: #000; }
    .quota-box { padding: 10px; border-radius: 5px; background: #fff3cd; border: 1px solid #ffeeba; margin-bottom: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# عرض الرصيد المتبقي للمستخدم في الجانب
st.sidebar.markdown(f"### رصيدك اليومي")
remaining = MAX_FREE_LIMIT - st.session_state['user_usage']
st.sidebar.progress(remaining / MAX_FREE_LIMIT)
st.sidebar.write(f"متبقي لك: {remaining} من {MAX_FREE_LIMIT} محاولات")

st.title("⚖️ منصة المُحكم الرقمي")

# --- 4. وظيفة التحليل الذكي (التنقل بين المفاتيح) ---
def ask_ai(prompt):
    # المحاولة الأولى: DeepSeek (لأنه الأقوى حالياً)
    try:
        ds_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
        response = ds_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        return response.choices[0].message.content
    except:
        # المحاولة الثانية: Google Gemini (إذا فشل الأول)
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except:
            # المحاولة الثالثة: Groq (إذا فشل الثاني)
            try:
                groq_client = Groq(api_key=GROQ_KEYS[0])
                chat = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                return chat.choices[0].message.content
            except:
                return "عذراً، جميع المحركات مزدحمة حالياً. يرجى المحاولة بعد قليل."

# --- واجهة المستخدم الرئيسية ---
countries = sorted([c.name for c in pycountry.countries])
country = st.selectbox("📍 اختر دولتك:", countries, index=countries.index("Yemen") if "Yemen" in countries else 0)
user_story = st.text_area("📝 اشرح قضيتك بالتفصيل:", height=150)

# اختيار المؤسسات (نفس الكود الخاص بك)
selected_insts = [] # سيتم ملؤها من اختياراتك السابقة

# التحقق من الرصيد قبل التحليل
if st.button("🚀 تحليل وحلول"):
    if st.session_state['user_usage'] >= MAX_FREE_LIMIT:
        st.error("⚠️ لقد استهلكت جميع محاولاتك المجانية لهذا اليوم. ننتظرك غداً!")
    elif not user_story.strip():
        st.warning("يرجى كتابة تفاصيل القضية أولاً.")
    else:
        with st.spinner("جاري التحليل باستخدام أقوى محركات الذكاء الاصطناعي..."):
            st.session_state['user_usage'] += 1
            full_prompt = f"أنت محامٍ خبير. الدولة: {country}. القضية: {user_story}. قدم حلولاً قانونية."
            result = ask_ai(full_prompt)
            st.markdown(f"<div class='report-card'>{result}</div>", unsafe_allow_html=True)
