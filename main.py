import streamlit as st
from groq import Groq
import pycountry
import os
from streamlit.components.v1 import html as components_html

# --- 1. كود توثيق ملكية جوجل (SEO) يوضع هنا في البداية ---
st.markdown('<meta name="google-site-verification" content="googlec310d9a33bd4047c" />', unsafe_allow_html=True)

# --- 2. إعدادات الصفحة ---
st.set_page_config(page_title="دليل القضائية العالمية والشخصية - محامي بين يديك", layout="centered")

# --- 3. التنسيق العربي والخط (CSS) ---
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

# إعداد عميل Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

st.title("⚖️ منصة المُحكم الرقمي")
st.markdown("""
منصة مساعدة قانونية ذكية — اختر دولتك والمؤسسات ذات الصلة، ثم اشرح قضيتك.
المنصة تقترح حلولاً وخطوات عملية لكنها لا تغني عن استشارة محامٍ مرخّص.
""")

# قائمة الدول
countries = sorted([c.name for c in pycountry.countries])
default_country = "Yemen" if "Yemen" in countries else countries[0]

country = st.selectbox("📍 اختر دولتك:", countries, index=countries.index(default_country))
user_story = st.text_area("📝 اشرح قضيتك بالتفصيل:", height=180)

# المؤسسات الدولية
INSTITUTIONS = [
    {"label": "الأمم المتحدة / UN", "key": "UN", "icon": os.path.join("assets","icons","UN.svg")},
    {"label": "المحكمة الجنائية الدولية / ICC", "key": "ICC", "icon": os.path.join("assets","icons","ICC.svg")},
    {"label": "منظمة التجارة العالمية / WTO", "key": "WTO", "icon": os.path.join("assets","icons","WTO.svg")},
    {"label": "منظمة الصحة العالمية / WHO", "key": "WHO", "icon": os.path.join("assets","icons","WHO.svg")},
    {"label": "البنك الدولي / World Bank", "key": "WorldBank", "icon": os.path.join("assets","icons","WorldBank.svg")},
    {"label": "صندوق النقد الدولي / IMF", "key": "IMF", "icon": os.path.join("assets","icons","IMF.svg")},
    {"label": "الاتحاد الأوروبي / EU", "key": "EU", "icon": os.path.join("assets","icons","EU.svg")},
    {"label": "الاتحاد الإفريقي / AU", "key": "AU", "icon": os.path.join("assets","icons","AU.svg")},
    {"label": "جامعة الدول العربية / Arab League", "key": "ArabLeague", "icon": os.path.join("assets","icons","ArabLeague.svg")},
    {"label": "الإنتربول / INTERPOL", "key": "INTERPOL", "icon": os.path.join("assets","icons","INTERPOL.svg")}
]

label_to_inst = {i["label"]: i for i in INSTITUTIONS}
st.markdown("**🏛️ اختر المؤسسات (انقر على مربع الاختيار تحت الأيقونة):**")
view_mode = st.radio("وضع العرض:", ["تلقائي", "كمبيوتر (3 أعمدة)", "هاتف (5 أعمدة)"], index=0, horizontal=True)

num_cols = 3
if view_mode == "تلقائي":
    params = st.experimental_get_query_params()
    if "cols" in params:
        num_cols = int(params["cols"][0])
    else:
        js = """
        <script>
        (function() {
          const cols = window.innerWidth <= 600 ? 5 : 3;
          const search = new URLSearchParams(window.location.search);
          search.set('cols', cols);
          window.location.search = '?' + search.toString();
        })();
        </script>
        """
        components_html(js, height=0)
elif view_mode.startswith("كمبيوتر"):
    num_cols = 3
else:
    num_cols = 5

cols = st.columns(num_cols)
for idx, inst in enumerate(INSTITUTIONS):
    col = cols[idx % num_cols]
    try:
        with open(inst["icon"], 'r', encoding='utf-8') as f:
            svg = f.read()
        col.markdown(f"<div class='inst-card'>{svg}<div class='inst-label'>{inst['label']}</div></div>", unsafe_allow_html=True)
    except Exception:
        col.markdown(f"<div class='inst-card'><div class='inst-label'>{inst['label']}</div></div>", unsafe_allow_html=True)
    col.checkbox("اختيار", key=f"inst_{inst['key']}")

selected_insts = [inst['label'] for inst in INSTITUTIONS if st.session_state.get(f"inst_{inst['key']}")]

include_international = st.checkbox("تضمين قوانين وأنظمة المؤسّسات الدولية في التحليل", value=True)
depth = st.radio("مستوى التوصيات:", ["نقاط سريعة", "خطة عمل مفصّلة", "مذكرة قانونية كاملة"], index=1)

if st.button("🚀 تحليل وحلول" ):
    if not user_story.strip():
        st.warning("يرجى كتابة تفاصيل القضية أولاً.")
    else:
        with st.spinner("جاري تحليل القضية..."):
            try:
                inst_text = ", ".join(selected_insts) if selected_insts else "لا مؤسسات محددة"
                prompt = f"أنت محامٍ قوي ومختص. القوانين المحلية: {country}. المؤسسات الدولية ذات الصلة: {inst_text}. القضية: {user_story}"
                chat = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "أنت محامٍ ذكي ودقيق."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    max_tokens=1500,
                )
                answer = chat.choices[0].message.content
                st.markdown(f"<div class='report-card'>{answer}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"خطأ: {str(e)}")

# --- باقي الكود الخاص بك (الفهرسة والمستندات) يظل كما هو دون تغيير ---
