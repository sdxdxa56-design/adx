import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import pycountry
import os

# Google Analytics (GA4) Measurement ID
GA_ID = "G-XVLFZ7M4WX"
components.html(f"""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_ID}');
</script>
""", height=0)

# Add Google Search Console meta verification in-page (may not be read if not injected into <head>)
st.markdown('<meta name="google-site-verification" content="c310d9a33bd4047c" />', unsafe_allow_html=True)

# إعدادات الصفحة
st.set_page_config(page_title="محامي بين يديك", layout="centered")

# التنسيق العربي والخط
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .report-card { background-color: #f8fafc; padding: 20px; border-radius: 10px; border-right: 6px solid #0f766e; color: #000; }
    .header { display:flex; gap:12px; align-items:center; }
    .logo { font-size:32px; }
    .small-muted { color:#6b7280; font-size:13px }
    .institution-badge { display:inline-block; padding:6px 10px; border-radius:999px; background:#eef2ff; margin:4px; }
    .inst-card { display:flex; flex-direction:column; align-items:center; padding:8px; border-radius:10px; transition: transform .12s ease, box-shadow .12s ease; }
    .inst-card:hover { transform: translateY(-6px); box-shadow: 0 10px 24px rgba(2,6,23,0.08); }
    .inst-card svg { width:64px; height:64px; }
    .inst-label { font-size:12px; margin-top:6px; text-align:center; }
    </style>
    """, unsafe_allow_html=True)

# إعداد عميل Groq — ضع المفتاح في المتغير البيئي GROQ_API_KEY
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

st.title("⚖️ منصة المُحكم الرقمي")
st.markdown("""
منصة مساعدة قانونية ذكية — اختر دولتك والمؤسسات ذات الصلة، ثم اشرح قضيتك.
المنصة تقترح حلولاً وخطوات عملية لكنها لا تغني عن استشارة محامٍ مرخّص.
""")
