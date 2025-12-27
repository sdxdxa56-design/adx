"""
main.py - الواجهة الرئيسية للمستخدمين
"""

import streamlit as st
import pycountry
import time
from datetime import datetime
from config import Config
from legal_advisor import legal_advisor
from database import Database
from retrieval_engine import RetrievalEngine

# إعدادات الصفحة
st.set_page_config(
    page_title="⚖️ منصة adx | المُحكم الرقمي",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحميل الأنظمة
db = Database()
retriever = RetrievalEngine()

# CSS مخصص
def load_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }}
    
    /* إخفاء عناصر Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stApp {{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}}
    
    /* كارد التحليل */
    .legal-card {{
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        border-right: 8px solid #4F46E5;
        animation: fadeIn 0.5s ease-in;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* شريط التقدم */
    .stProgress > div > div > div > div {{
        background-color: #4F46E5;
    }}
    
    /* الأيقونات */
    .institution-icon {{
        width: 80px;
        height: 80px;
        border-radius: 16px;
        padding: 15px;
        margin: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    .institution-icon:hover {{
        transform: translateY(-5px);
        border-color: #4F46E5;
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.2);
    }}
    
    .institution-icon.selected {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #4F46E5;
    }}
    
    /* زر التحليل */
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 40px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
    }}
    
    /* الشريط الجانبي */
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }}
    
    </style>
    """, unsafe_allow_html=True)

# تهيئة الجلسة
def init_session():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}_{random.randint(1000, 9999)}"
    
    if 'usage_count' not in st.session_state:
        st.session_state.usage_count = 0
    
    if 'selected_institutions' not in st.session_state:
        st.session_state.selected_institutions = []
    
    if 'country' not in st.session_state:
        st.session_state.country = "Yemen"

# شريط اختيار الدولة
def country_selector():
    st.sidebar.markdown("### 🌍 اختر دولتك")
    
    # ترتيب الدول العربية أولاً
    arab_countries = ["Yemen", "Saudi Arabia", "Egypt", "United Arab Emirates", 
                     "Qatar", "Jordan", "Kuwait", "Oman", "Bahrain", "Lebanon"]
    
    all_countries = sorted([c.name for c in pycountry.countries])
    
    # نقل الدول العربية للأعلى
    for country in arab_countries:
        if country in all_countries:
            all_countries.remove(country)
            all_countries.insert(0, country)
    
    country = st.sidebar.selectbox(
        "الدولة:",
        all_countries,
        index=all_countries.index("Yemen") if "Yemen" in all_countries else 0,
        label_visibility="collapsed"
    )
    
    st.session_state.country = country
    
    # عرض معلومات الدولة
    if country in Config.SUPPORTED_COUNTRIES:
        info = Config.SUPPORTED_COUNTRIES[country]
        st.sidebar.info(f"**النظام القانوني:** {info['legal_system']}")
    
    return country

# شريط اختيار المؤسسات
def institution_selector():
    st.sidebar.markdown("### 🏛️ اختر المؤسسات الدولية")
    
    institutions = Config.INTERNATIONAL_INSTITUTIONS
    
    # عرض المؤسسات على شكل أيقونات
    cols = st.sidebar.columns(3)
    
    for idx, (key, inst) in enumerate(institutions.items()):
        col_idx = idx % 3
        
        with cols[col_idx]:
            # محاولة تحميل الأيقونة
            try:
                icon_path = f"{Config.ICONS_DIR}/{inst['icon']}"
                with open(icon_path, "r") as f:
                    icon_svg = f.read()
                    
                # إنشاء بطاقة المؤسسة
                is_selected = key in st.session_state.selected_institutions
                
                st.markdown(f"""
                <div class="institution-icon {'selected' if is_selected else ''}" 
                     onclick="this.classList.toggle('selected')">
                    <center>
                        {icon_svg}
                        <p style="margin-top: 8px; font-size: 12px;">{inst['name']}</p>
                    </center>
                </div>
                """, unsafe_allow_html=True)
                
                # زر الاختيار
                if st.checkbox("", key=f"inst_{key}", value=is_selected):
                    if key not in st.session_state.selected_institutions:
                        st.session_state.selected_institutions.append(key)
                else:
                    if key in st.session_state.selected_institutions:
                        st.session_state.selected_institutions.remove(key)
                        
            except:
                # إذا فشل تحميل الأيقونة
                if st.checkbox(inst['name'], key=f"inst_{key}"):
                    if key not in st.session_state.selected_institutions:
                        st.session_state.selected_institutions.append(key)
                else:
                    if key in st.session_state.selected_institutions:
                        st.session_state.selected_institutions.remove(key)

# واجهة المستخدم الرئيسية
def main():
    load_css()
    init_session()
    
    # الهيدر
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="color: white; font-size: 3.5rem; margin-bottom: 10px;">⚖️ المُحكم الرقمي</h1>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.2rem;">
            مستشارك القانوني الذكي • تحليل قضايا • حلول عملية • دعم دولي
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # الشريط الجانبي
    with st.sidebar:
        country = country_selector()
        institution_selector()
        
        # عداد الاستخدام
        st.sidebar.markdown("---")
        remaining = Config.MAX_REQUESTS_PER_USER - st.session_state.usage_count
        st.sidebar.markdown(f"### 📊 رصيدك اليومي")
        st.sidebar.progress(remaining / Config.MAX_REQUESTS_PER_USER)
        st.sidebar.markdown(f"**{remaining}** من **{Config.MAX_REQUESTS_PER_USER}** محاولات متبقية")
        
        # زر المساعدة
        if st.sidebar.button("🆘 مساعدة سريعة"):
            st.sidebar.info("""
            **كيفية الاستخدام:**
            1. اختر دولتك
            2. اختر المؤسسات الدولية
            3. اشرح مشكلتك
            4. اضغط على زر التحليل
            
            **ملاحظة:** المنصة تقدم استشارات أولية ولا تغني عن المحامي.
            """)
    
    # المنطقة الرئيسية
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 اشرح قضيتك بالتفصيل")
        
        # خيارات إضافية
        with st.expander("⚙️ إعدادات متقدمة"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                analysis_depth = st.select_slider(
                    "مستوى التحليل:",
                    options=["سريع", "متوسط", "تفصيلي"],
                    value="متوسط"
                )
                
            with col_b:
                include_local = st.checkbox("تضمين القوانين المحلية", value=True)
                include_international = st.checkbox("تضمين القوانين الدولية", value=True)
        
        # حقل النص
        user_issue = st.text_area(
            "اكتب مشكلتك القانونية:",
            height=200,
            placeholder="مثال: لدي نزاع مع شركة حول عقد عمل...",
            help="اكتب بأكبر قدر من التفاصيل مع ذكر التواريخ والأطراف"
        )
        
        # زر التحليل
        analyze_btn = st.button(
            "🚀 بدأ التحليل القانوني",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.markdown("### 💡 نصائح سريعة")
        
        tips = [
            "📌 اذكر جميع الأطراف بأسمائهم",
            "📅 حدد التواريخ المهمة",
            "📄 أرفق أرقام العقود إذا وجدت",
            "⚖️ حدد نوع القضية (مدني، جنائي، تجاري)",
            "🌍 اختر المؤسسات المناسبة لنوع القضية",
            "⏱️ تحلى بالصفح قد تستغرق بعض القضايا وقتاً"
        ]
        
        for tip in tips:
            st.info(tip)
        
        # بحث في القوانين
        st.markdown("### 🔍 ابحث في القوانين")
        search_query = st.text_input("اكتب كلمة للبحث:")
        
        if search_query:
            with st.spinner("جاري البحث..."):
                results = retriever.search(search_query, country)
                if results:
                    for result in results[:3]:
                        st.markdown(f"**{result['title']}**")
                        st.caption(result['preview'][:100] + "...")
                        st.markdown("---")
    
    # التحليل
    if analyze_btn and user_issue:
        if st.session_state.usage_count >= Config.MAX_REQUESTS_PER_USER:
            st.error("""
            ⚠️ لقد استهلكت جميع المحاولات المجانية لهذا اليوم
            
            **الحلول المقترحة:**
            1. عد غداً للمزيد من المحاولات
            2. ترقى إلى الإصدار المميز
            3. اتصل بمكتب محاماة متخصص
            """)
            
        elif len(user_issue.strip()) < 50:
            st.warning("يرجى كتابة وصف مفصل للمشكلة (50 حرف على الأقل)")
            
        else:
            # زيادة العداد
            st.session_state.usage_count += 1
            
            # تسجيل في قاعدة البيانات
            db.record_usage(
                user_id=st.session_state.user_id,
                country=country,
                issue_length=len(user_issue),
                institutions=st.session_state.selected_institutions
            )
            
            # عرض شريط التقدم
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                progress_bar.progress(i + 1)
                status_text.text(f"جاري التحليل... {i+1}%")
                time.sleep(0.01)
            
            # الحصول على التحليل
            with st.spinner("🔄 جاري استشارة الخبراء القانونيين..."):
                try:
                    analysis = legal_advisor.get_intelligent_response(
                        country=country,
                        issue=user_issue,
                        institutions=st.session_state.selected_institutions,
                        include_international=include_international
                    )
                    
                    # عرض النتائج
                    st.markdown("---")
                    st.markdown("## 📋 نتائج التحليل القانوني")
                    
                    # كارد التحليل
                    st.markdown(f"""
                    <div class="legal-card">
                        <h3>⚖️ التحليل القانوني</h3>
                        <p>{analysis['analysis']}</p>
                        
                        <h3>💡 الحلول المقترحة</h3>
                        <ul>
                            {''.join([f'<li>{sol}</li>' for sol in analysis['suggested_solutions'][:5]])}
                        </ul>
                        
                        <h3>📋 الخطوات العملية</h3>
                        <ol>
                            {''.join([f'<li>{step}</li>' for step in analysis['steps'][:5]])}
                        </ol>
                        
                        <h3>⚠️ تحذيرات هامة</h3>
                        <ul>
                            {''.join([f'<li style="color: #ef4444;">{warn}</li>' for warn in analysis['warnings'][:3]])}
                        </ul>
                        
                        <div style="background: #f3f4f6; padding: 15px; border-radius: 10px; margin-top: 20px;">
                            <p><strong>👤 المحامي الافتراضي:</strong> {analysis['used_model']}</p>
                            <p><strong>📊 درجة الثقة:</strong> {analysis['confidence']:.0%}</p>
                            <p><small>🕒 وقت التحليل: {datetime.now().strftime('%H:%M')}</small></p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # خيارات إضافية
                    with st.expander("📄 المستندات المطلوبة"):
                        for doc in analysis.get('documents', []):
                            st.markdown(f"- {doc}")
                    
                    with st.expander("🏢 الجهات المختصة"):
                        for auth in analysis.get('authorities', []):
                            st.markdown(f"- {auth}")
                    
                    # تحميل النتائج
                    result_text = f"""
                    تحليل قانوني - {country}
                    التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    
                    {analysis['analysis']}
                    
                    الحلول:
                    {chr(10).join(analysis['suggested_solutions'])}
                    """
                    
                    st.download_button(
                        label="📥 تحميل التحليل",
                        data=result_text,
                        file_name=f"تحليل_قانوني_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"""
                    حدث خطأ أثناء التحليل:
                    {str(e)}
                    
                    **يرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني.**
                    """)
            
            # إعادة تعيين شريط التقدم
            progress_bar.empty()
            status_text.empty()
    
    # الفوتر
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.6); padding: 20px;">
        <p>⚖️ منصة adx - المُحكم الرقمي © 2024</p>
        <p><small>هذه المنصة تقدم استشارات قانونية أولية ولا تغني عن استشارة محامٍ مرخص</small></p>
        <p><small>معلومات الاتصال: support@adx-platform.com</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()