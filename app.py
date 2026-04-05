import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Grand Ceram Maintenance Pro",
    page_icon="⚙️",
    layout="wide"
)

# رابط البيانات (CSV) للقراءة
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4E-4aLeigAD1Ehm9OMV8Jwguai9H0wPJH7Z6alA528mE6I2ZFBXH9oDjo1T_UoWVW8nurahgyWUfM/pub?output=csv"

# رابط جوجل فورم الخاص بك (للكتابة)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/1yiAXME-nXY9Sf5FbFXnKl6cdA7p_GCIm0ZeCRSi_NEI/viewform?embedded=true"

# --- 2. نظام المستخدمين ---
USER_DB = {
    "admin": {"pw": "gc2026", "role": "المدير التقني"},
    "wail": {"pw": "wail88", "role": "مسؤول المخازن"},
    "maint": {"pw": "maint123", "role": "قسم الصيانة"},
    "chef": {"pw": "chef01", "role": "رئيس الورشة"},
}

ATELIERS = ["Atelier Presse", "Atelier Four", "Atelier Selection", "Atelier PMP", "Atelier PEC", "Atelier LINGE"]

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

tabs = st.tabs(["📊 سجل الأعطال (صيانة)", "🚨 تبليغ جديد (ورشة)"])

# --- التبويب 1: لوحة تحكم الصيانة ---
with tabs[0]:
    try:
        df = pd.read_csv(SHEET_URL)
        st.subheader("📋 قائمة التدخلات التقنية الجارية")
        
        if not df.empty:
            # فلتر الورشات
            selected = st.multiselect("تصفية حسب الورشة:", ATELIERS, default=ATELIERS)
            
            # البحث عن عمود الورشة (جوجل فورم غالباً يسميه باسم السؤال)
            # سنحاول العثور على أي عمود يحتوي على كلمة 'Atelier'
            atelier_col = [c for c in df.columns if 'Atelier' in c or 'الورشة' in c]
            
            if atelier_col:
                filtered_df = df[df[atelier_col[0]].isin(selected)]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد بلاغات مسجلة حالياً.")
            
        if st.button("🔄 تحديث البيانات الآن"):
            st.rerun()
            
    except Exception as e:
        st.error(f"⚠️ خطأ في جلب البيانات: {e}")

# --- التبويب 2: نموذج التبليغ (Google Form) ---
with tabs[1]:
    if st.session_state.role in ["رئيس الورشة", "المدير التقني"]:
        st.subheader("📝 إرسال بلاغ عطل فوري")
        st.info("قم بملء الخانات أدناه واضغط Submit ليتم إرسالها لجدول الصيانة.")
        # دمج الفورم داخل التطبيق
        st.components.v1.iframe(GOOGLE_FORM_URL, height=700, scrolling=True)
    else:
        st.warning("⚠️ هذه الصلاحية مخصصة لرؤساء الورشات فقط.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Grand Ceram Pro v2.0 - {datetime.now().year}")
