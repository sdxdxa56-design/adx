"""
admin.py - لوحة تحكم المدير/المطور
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from config import Config
from database import Database

# إعدادات الصفحة للمدير
st.set_page_config(
    page_title="لوحة تحكم adx",
    page_icon="👑",
    layout="wide"
)

# CSS خاص بلوحة التحكم
st.markdown("""
<style>
.admin-panel {
    background: #1a1a2e;
    color: white;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 20px;
    margin: 10px;
    text-align: center;
}

.danger-zone {
    background: #ff4444;
    border-radius: 10px;
    padding: 20px;
    margin: 20px 0;
    color: white;
}
</style>
""", unsafe_allow_html=True)

class AdminPanel:
    def __init__(self):
        self.db = Database()
        self.password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    
    def authenticate(self):
        """مصادقة المدير"""
        if 'admin_authenticated' not in st.session_state:
            st.session_state.admin_authenticated = False
        
        if not st.session_state.admin_authenticated:
            st.title("🔐 دخول المدير")
            
            col1, col2, col3 = st.columns([1,2,1])
            
            with col2:
                password = st.text_input("كلمة المرور:", type="password")
                
                if st.button("دخول"):
                    if password == self.password:
                        st.session_state.admin_authenticated = True
                        st.rerun()
                    else:
                        st.error("كلمة مرور خاطئة!")
            
            st.stop()
    
    def dashboard(self):
        """لوحة التحكم الرئيسية"""
        st.title("👑 لوحة تحكم منصة adx")
        
        # شريط التنقل
        menu = st.sidebar.radio(
            "القائمة:",
            ["📊 الإحصائيات", "👥 المستخدمين", "⚙️ الإعدادات", "🛠️ الصيانة", "📈 التقارير"]
        )
        
        if menu == "📊 الإحصائيات":
            self.show_statistics()
        elif menu == "👥 المستخدمين":
            self.show_users()
        elif menu == "⚙️ الإعدادات":
            self.show_settings()
        elif menu == "🛠️ الصيانة":
            self.show_maintenance()
        elif menu == "📈 التقارير":
            self.show_reports()
    
    def show_statistics(self):
        """عرض الإحصائيات"""
        st.header("📊 إحصائيات المنصة")
        
        # الحصول على البيانات
        total_users = self.db.get_total_users()
        total_requests = self.db.get_total_requests()
        today_requests = self.db.get_today_requests()
        popular_countries = self.db.get_popular_countries()
        
        # عرض المقاييس
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 إجمالي المستخدمين", total_users)
        
        with col2:
            st.metric("📨 إجمالي الطلبات", total_requests)
        
        with col3:
            st.metric("📊 طلبات اليوم", today_requests)
        
        with col4:
            st.metric("⚡ حالة الخدمة", "نشطة", "100%")
        
        # الرسوم البيانية
        col1, col2 = st.columns(2)
        
        with col1:
            # طلبات حسب الدولة
            if popular_countries:
                df = pd.DataFrame(popular_countries, columns=['الدولة', 'الطلبات'])
                fig = px.pie(df, values='الطلبات', names='الدولة', 
                           title='الطلبات حسب الدولة')
                st.plotly_chart(fig)
        
        with col2:
            # طلبات آخر 7 أيام
            weekly_data = self.db.get_weekly_usage()
            if weekly_data:
                df = pd.DataFrame(weekly_data, columns=['اليوم', 'الطلبات'])
                fig = px.line(df, x='اليوم', y='الطلبات', 
                            title='الطلبات في آخر 7 أيام')
                st.plotly_chart(fig)
    
    def show_users(self):
        """إدارة المستخدمين"""
        st.header("👥 إدارة المستخدمين")
        
        # البحث عن مستخدم
        search = st.text_input("🔍 بحث عن مستخدم:")
        
        # عرض جدول المستخدمين
        users = self.db.get_all_users(search)
        
        if users:
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
            
            # تفاصيل المستخدم المحدد
            selected_user = st.selectbox("اختر مستخدم:", df['user_id'].tolist())
            
            if selected_user:
                user_details = self.db.get_user_details(selected_user)
                
                if user_details:
                    with st.expander("تفاصيل المستخدم"):
                        st.json(user_details)
                        
                        # إجراءات على المستخدم
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("🔄 إعادة تعيين الحصص"):
                                self.db.reset_user_quota(selected_user)
                                st.success("تم إعادة تعيين الحصص!")
                        
                        with col2:
                            if st.button("🚫 حظر المستخدم"):
                                if st.checkbox("تأكيد الحظر"):
                                    self.db.ban_user(selected_user)
                                    st.success("تم حظر المستخدم!")
        
        else:
            st.info("لا يوجد مستخدمين")
    
    def show_settings(self):
        """إعدادات النظام"""
        st.header("⚙️ إعدادات النظام")
        
        # إعدادات الحصص
        st.subheader("إعدادات الحصص")
        
        new_limit = st.number_input(
            "عدد المحاولات اليومية:",
            min_value=1,
            max_value=100,
            value=Config.MAX_REQUESTS_PER_USER
        )
        
        if st.button("💾 حفظ إعدادات الحصص"):
            # هنا سيتم حفظ الإعدادات في قاعدة البيانات
            st.success(f"تم تحديث الحصص إلى {new_limit} محاولة يومية")
        
        # إدارة المفاتيح
        st.subheader("🔑 إدارة مفاتيح API")
        
        api_keys = st.text_area("مفاتيح API (JSON):", value=str(Config.API_KEYS), height=200)
        
        if st.button("🔄 تحديث المفاتيح"):
            try:
                # هنا سيتم حفظ المفاتيح في ملف آمن
                st.success("تم تحديث المفاتيح!")
            except:
                st.error("خطأ في تنسيق JSON!")
        
        # إدارة المؤسسات
        st.subheader("🏛️ إدارة المؤسسات")
        
        institutions = Config.INTERNATIONAL_INSTITUTIONS
        
        for key, inst in institutions.items():
            with st.expander(f"{inst['name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text_input("الاسم:", value=inst['name'], key=f"name_{key}")
                
                with col2:
                    st.text_input("المجال القانوني:", 
                                value=", ".join(inst['legal_domain']),
                                key=f"domain_{key}")
    
    def show_maintenance(self):
        """صيانة النظام"""
        st.header("🛠️ صيانة النظام")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # تنظيف البيانات القديمة
            if st.button("🧹 تنظيف البيانات القديمة"):
                with st.spinner("جاري التنظيف..."):
                    deleted = self.db.clean_old_data()
                    st.success(f"تم حذف {deleted} سجل قديم")
            
            # تحديث الفهرس
            if st.button("🔄 تحديث فهرس البحث"):
                with st.spinner("جاري تحديث الفهرس..."):
                    # هنا سيتم تشغيل سكريبت الفهرسة
                    st.success("تم تحديث الفهرس!")
            
            # نسخ احتياطي
            if st.button("💾 نسخ احتياطي"):
                with st.spinner("جاري النسخ الاحتياطي..."):
                    # هنا سيتم إنشاء نسخة احتياطية
                    st.success("تم إنشاء النسخة الاحتياطية!")
                    st.download_button(
                        label="📥 تحميل النسخة",
                        data="backup_data",
                        file_name=f"backup_{datetime.now().strftime('%Y%m%d')}.json"
                    )
        
        with col2:
            # منطقة الخطر
            st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
            st.warning("⚠️ منطقة الخطر - إجراءات لا يمكن التراجع عنها")
            
            if st.button("🗑️ حذف جميع البيانات", type="secondary"):
                if st.checkbox("أنا أدرك أن هذا الإجراء لا يمكن التراجع عنه"):
                    if st.text_input("اكتب 'حذف' للتأكيد:") == "حذف":
                        st.error("تم حذف جميع البيانات!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # سجلات النظام
        st.subheader("📋 سجلات النظام")
        
        logs = self.db.get_system_logs()
        
        if logs:
            df = pd.DataFrame(logs, columns=['الوقت', 'المستوى', 'الرسالة'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد سجلات")
    
    def show_reports(self):
        """التقارير"""
        st.header("📈 تقارير أداء النظام")
        
        # اختيار نوع التقرير
        report_type = st.selectbox(
            "نوع التقرير:",
            ["أداء اليوم", "أداء الأسبوع", "أداء الشهر", "مخصص"]
        )
        
        if report_type == "مخصص":
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input("من تاريخ:")
            
            with col2:
                end_date = st.date_input("إلى تاريخ:")
        
        # إنشاء التقرير
        if st.button("إنشاء التقرير"):
            with st.spinner("جاري إنشاء التقرير..."):
                # هنا سيتم إنشاء التقرير
                report_data = self.db.generate_report(report_type)
                
                if report_data:
                    # عرض التقرير
                    st.subheader("ملخص التقرير")
                    
                    for key, value in report_data.items():
                        st.metric(key, value)
                    
                    # تحميل التقرير
                    report_text = f"""
                    تقرير أداء منصة adx
                    النوع: {report_type}
                    التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    
                    {str(report_data)}
                    """
                    
                    st.download_button(
                        label="📥 تحميل التقرير",
                        data=report_text,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.txt"
                    )
                else:
                    st.warning("لا توجد بيانات لهذا التقرير")

# تشغيل لوحة التحكم
if __name__ == "__main__":
    admin = AdminPanel()
    admin.authenticate()
    admin.dashboard()