import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Grand Ceram Maintenance Pro",
    page_icon="⚙️",
    layout="wide"
)

# الرابط الجديد الذي أرسلته (ورقة الردود)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStO5FalGVSBXYzvsCSOJ7CAXaQ1iIZsdSIcYFwnY5j2aQ_1_-QYxHV8kk2NmXKO9q8iCU62q0zZS75/pub?output=csv"

# رابط جوجل فورم الخاص بك
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/1yiAXME-nXY9Sf5FbFXnKl6cdA7p_GCIm0ZeCRSi_NEI/viewform?embedded=true"

# --- 2. نظام المستخدمين ---
USER_DB = {
    "admin": {"pw": "gc2026", "role": "المدير التقني"},
    "wail": {"pw": "wail88", "role": "مسؤول المخازن"},
    "maint": {"pw": "maint123", "role": "قسم الصيانة"},
    "chef": {"pw": "chef01", "role": "رئيس الورشة"},
}

# --- 3. إدارة الجلسة ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# واجهة تسجيل الدخول
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔐 دخول نظام Grand Ceram")
        with st.form("login_form"):
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                if u in USER_DB and USER_DB[u]["pw"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = USER_DB[u]["role"]
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
    st.stop()

# --- 4. واجهة التطبيق الرئيسية ---
st.sidebar.title(f"👤 {st.session_state.role}")
st.sidebar.write(f"المستخدم: {st.session_state.user}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🛠️ نظام إدارة صيانة SARL Grand Ceram")
st.divider()

tabs = st.tabs(["📊 سجل الأعطال المبلغ عنها", "🚨 إرسال تبليغ جديد"])

# --- التبويب 1: لوحة تحكم الصيانة (قراءة البيانات) ---
with tabs[0]:
    try:
        # قراءة البيانات مع إلغاء التخزين المؤقت لضمان التحديث
        df = pd.read_csv(SHEET_URL)
        
        st.subheader("📋 قائمة التنبيهات المستلمة من الورشات")
        
        if not df.empty:
            # عرض البيانات كاملة كما تأتي من جوجل فورم
            st.dataframe(df, use_container_width=True)
            
            st.info(f"عدد البلاغات الإجمالي: {len(df)}")
        else:
            st.warning("⚠️ الجدول متصل ولكن لا توجد بيانات مسجلة في ملف الإكسل حتى الآن.")
            
        if st.button("🔄 تحديث البيانات (Refresh)"):
            st.cache_data.clear()
            st.rerun()
            
    except Exception as e:
        st.error(f"⚠️ فشل في الاتصال بورقة البيانات: {e}")
        st.info("تأكد من أنك قمت بنشر 'ورقة الردود' (Form Responses) تحديداً بصيغة CSV.")

# --- التبويب 2: نموذج التبليغ (Google Form) ---
with tabs[1]:
    if st.session_state.role in ["رئيس الورشة", "المدير التقني"]:
        st.subheader("📝 نموذج التبليغ الفوري")
        st.markdown("---")
        # دمج الفورم داخل التطبيق
        st.components.v1.iframe(GOOGLE_FORM_URL, height=800, scrolling=True)
    else:
        st.warning("⚠️ هذه الصلاحية مخصصة لرؤساء الورشات لإرسال البلاغات.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Grand Ceram Pro v2.1")
