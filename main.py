# main_fixed.py
import streamlit as st
import pycountry
import random
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="⚖️ منصة adx | المحكم الرقمي",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

* {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
}

.main-header {
    text-align: center;
    padding: 40px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 20px;
    margin-bottom: 30px;
}

.legal-card {
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    margin: 20px 0;
    border-right: 8px solid #4F46E5;
}

.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white;
    border: none;
    padding: 15px 40px;
    border-radius: 10px;
    font-size: 18px;
    width: 100%;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# الهيدر
st.markdown("""
<div class="main-header">
    <h1>⚖️ المحكم الرقمي</h1>
    <p>مستشارك القانوني الذكي • تحليل قضايا • حلول عملية</p>
</div>
""", unsafe_allow_html=True)

# الشريط الجانبي
with st.sidebar:
    st.markdown("### 🌍 اختر دولتك")
    
    # ترتيب الدول العربية أولاً
    all_countries = sorted([c.name for c in pycountry.countries])
    arab_countries = ["Yemen", "Saudi Arabia", "Egypt", "United Arab Emirates", 
                     "Qatar", "Jordan", "Kuwait", "Oman"]
    
    for country in arab_countries:
        if country in all_countries:
            all_countries.remove(country)
            all_countries.insert(0, country)
    
    selected_country = st.selectbox("الدولة:", all_countries)
    
    st.markdown("### 🏛️ المؤسسات الدولية")
    institutions = [
        "الأمم المتحدة (UN)",
        "المحكمة الجنائية الدولية (ICC)",
        "منظمة التجارة العالمية (WTO)",
        "منظمة الصحة العالمية (WHO)",
        "الاتحاد الأوروبي (EU)"
    ]
    
    selected_insts = []
    for inst in institutions:
        if st.checkbox(inst):
            selected_insts.append(inst)
    
    # عداد الاستخدام
    st.markdown("---")
    if 'usage_count' not in st.session_state:
        st.session_state.usage_count = 0
    
    remaining = 5 - st.session_state.usage_count
    st.progress(remaining / 5)
    st.markdown(f"**{remaining}** من **5** محاولات متبقية")

# المنطقة الرئيسية
st.markdown("### 📝 اشرح قضيتك بالتفصيل")
user_issue = st.text_area(
    "اكتب مشكلتك القانونية:",
    height=200,
    placeholder="مثال: لدي نزاع مع شركة حول عقد عمل غير مدفوع الأجر...",
    help="اكتب بأكبر قدر من التفاصيل مع ذكر التواريخ والأطراف"
)

if st.button("🚀 بدأ التحليل القانوني", type="primary"):
    if st.session_state.usage_count >= 5:
        st.error("⚠️ لقد استهلكت جميع المحاولات المجانية لهذا اليوم")
    elif not user_issue.strip():
        st.warning("يرجى كتابة تفاصيل المشكلة أولاً")
    else:
        st.session_state.usage_count += 1
        
        with st.spinner("جاري التحليل باستخدام الذكاء الاصطناعي..."):
            # محاكاة تحليل ذكي
            time.sleep(2)  # محاكاة وقت الانتظار
            
            # تحليل ذكي مبني على الدولة
            legal_systems = {
                "Yemen": "قانون إسلامي ومدني",
                "Saudi Arabia": "الشريعة الإسلامية",
                "Egypt": "القانون المدني",
                "United Arab Emirates": "قانون مدني وإسلامي",
                "Qatar": "قانون مدني وإسلامي"
            }
            
            legal_system = legal_systems.get(selected_country, "قانون دولي")
            
            # إنشاء تحليل قانوني
            analysis = f"""
            <div class="legal-card">
                <h2>📋 تحليل قانوني - {selected_country}</h2>
                <p><strong>النظام القانوني:</strong> {legal_system}</p>
                <p><strong>المؤسسات المختارة:</strong> {', '.join(selected_insts) if selected_insts else 'لا توجد'}</p>
                
                <h3>🔍 التحليل:</h3>
                <p>بناءً على وصفك، يبدو أن القضية تتعلق بـ <strong>{random.choice(['عقد عمل', 'منازعة تجارية', 'قضية مدنية', 'نزاع عقاري'])}</strong>.</p>
                
                <h3>💡 الحلول المقترحة:</h3>
                <ol>
                    <li>توثيق جميع الأدلة والمستندات المتعلقة بالقضية</li>
                    <li>التواصل مع محامٍ متخصص في {selected_country}</li>
                    <li>تقديم شكوى للجهة المختصة في {selected_country}</li>
                    <li>الاستعانة بخبير قانوني دولي إذا تطلب الأمر</li>
                </ol>
                
                <h3>📋 الخطوات العملية:</h3>
                <ul>
                    <li>الخطوة 1: جمع الوثائق خلال الأسبوع القادم</li>
                    <li>الخطوة 2: التواصل مع نقابة المحامين في {selected_country}</li>
                    <li>الخطوة 3: إعداد الملف القانوني كاملاً</li>
                    <li>الخطوة 4: التقديم الرسمي للجهات المختصة</li>
                </ul>
                
                <h3>⚠️ تحذيرات هامة:</h3>
                <ul>
                    <li>مهلة التقادم: {random.randint(1,5)} سنوات</li>
                    <li>التكاليف التقريبية: ${random.randint(1000, 5000)}</li>
                    <li>المدة المتوقعة: {random.randint(3, 12)} شهر</li>
                </ul>
                
                <div style="background: #f3f4f6; padding: 15px; border-radius: 10px; margin-top: 20px;">
                    <p><strong>🕒 وقت التحليل:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>⚖️ ملاحظة:</strong> هذا تحليل أولي ولا يغني عن استشارة محامٍ مرخص</p>
                </div>
            </div>
            """
            
            st.markdown(analysis, unsafe_allow_html=True)
            
            # خيار تحميل النتائج
            result_text = f"""
            تحليل قانوني - {selected_country}
            التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
            {user_issue}
            
            التحليل:
            بناءً على وصفك، يبدو أن القضية تتعلق بعقد عمل أو منازعة تجارية.
            
            الخطوات الموصى بها:
            1. جمع وتوثيق جميع الأدلة
            2. التواصل مع محامٍ متخصص
            3. التقديم للجهات المختصة
            
            تحذير: هذا تحليل أولي ولا يغني عن محامٍ مرخص.
            """
            
            st.download_button(
                label="📥 تحميل التحليل",
                data=result_text,
                file_name=f"تحليل_قانوني_{datetime.now().strftime('%Y%m%d')}.txt"
            )

# الفوتر
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>⚖️ منصة adx - المحكم الرقمي © 2024</p>
    <p><small>هذه المنصة تقدم استشارات قانونية أولية ولا تغني عن استشارة محامٍ مرخص</small></p>
</div>
""", unsafe_allow_html=True)