import streamlit as st
from groq import Groq

# إعدادات الصفحة
st.set_page_config(page_title="المُحكم الرقمي", layout="centered")

# التنسيق العربي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .report-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-right: 5px solid #1e3a8a; color: #000; }
    </style>
    """, unsafe_allow_html=True)

# الاتصال بالذكاء الاصطناعي (ضع مفتاحك هنا)
client = Groq(api_key="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")

st.title("⚖️ منصة المُحكم الرقمي")
st.write("استشارة قانونية فورية مدعومة بالذكاء الاصطناعي")

country = st.text_input("📍 الدولة المعنية:", value="اليمن")
user_story = st.text_area("📝 اشرح قضيتك بالتفصيل:", height=150)

if st.button("🚀 بدء التحليل"):
    if user_story:
        with st.spinner("جاري التحليل..."):
            try:
                # تحديث الموديل المطلوب
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"أنت محكم قانوني في {country}. حلل هذه القضية: {user_story}"}],
                    model="llama-3.3-70b-versatile",
                )
                st.markdown(f"<div class='report-card'>{chat.choices[0].message.content}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"خطأ: {str(e)}")
    else:
        st.warning("يرجى كتابة تفاصيل القضية.")
