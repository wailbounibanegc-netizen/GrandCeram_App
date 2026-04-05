import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات التطبيق ---
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="⚙️", layout="wide")

# رابط البيانات (للقراءة)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4E-4aLeigAD1Ehm9OMV8Jwguai9H0wPJH7Z6alA528mE6I2ZFBXH9oDjo1T_UoWVW8nurahgyWUfM/pub?output=csv"

# --- قاعدة بيانات المستخدمين (يمكنك نقلها لاحقاً لملف Secrets) ---
USER_DB = {
    "admin": {"pw": "gc2026", "role": "المدير التقني"},
    "wail": {"pw": "wail88", "role": "مسؤول المخازن"},
    "maintenance": {"pw": "maint123", "role": "قسم الصيانة"},
    "chef_presse": {"pw": "presse01", "role": "رئيس الورشة"},
}

ATELIERS = ["Atelier Presse", "Atelier Four", "Atelier Selection", "Atelier PMP", "Atelier PEC", "Atelier LINGE"]

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول - Grand Ceram Pro")
    with st.center():
        with st.form("login"):
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                if u in USER_DB and USER_DB[u]["pw"] == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = USER_DB[u]["role"]
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة")
    st.stop()

# --- واجهة التطبيق الرئيسية (بعد الدخول) ---
st.sidebar.title(f"👤 {st.session_state.role}")
st.sidebar.write(f"مرحباً: {st.session_state.user}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🛠️ نظام إدارة صيانة مصنع Grand Ceram")
tabs = st.tabs(["📊 لوحة التحكم", "🚨 تبليغ عن عطل", "🔧 تحديث المهام"])

# --- التبويب 1: لوحة التحكم (متاحة للجميع) ---
with tabs[0]:
    try:
        df = pd.read_csv(SHEET_URL)
        st.subheader("حالة الورشات الحالية")
        
        # تصفية حسب الورشة
        atelier_filter = st.multiselect("اختر الورشة:", ATELIERS, default=ATELIERS)
        filtered_df = df[df['Atelier'].isin(atelier_filter)]
        
        st.dataframe(filtered_df, use_container_width=True)
    except:
        st.info("لا توجد بيانات حالياً. ابدأ بإضافة بلاغ.")

# --- التبويب 2: التبليغ (متاح لرئيس الورشة والمدير) ---
with tabs[1]:
    if st.session_state.role in ["رئيس الورشة", "المدير التقني"]:
        st.subheader("📝 إرسال بلاغ صيانة جديد")
        with st.form("report_form"):
            col1, col2 = st.columns(2)
            with col1:
                at = st.selectbox("الورشة", ATELIERS)
                mc = st.text_input("الآلة")
            with col2:
                pr = st.selectbox("الأولوية", ["عادي", "متوسط", "عاجل (توقف إنتاج)"])
                desc = st.text_area("وصف العطل")
            
            if st.form_submit_button("إرسال البلاغ"):
                # هنا يجب ربط Google Apps Script لإرسال البيانات فعلياً
                st.success("تم إرسال البلاغ بنجاح للفريق التقني!")
    else:
        st.warning("عذراً، ليس لديك صلاحية لإرسال بلاغات. هذه الميزة خاصة برؤساء الورشات.")

# --- التبويب 3: تحديث المهام (خاص بقسم الصيانة والمدير التقني) ---
with tabs[2]:
    if st.session_state.role in ["قسم الصيانة", "المدير التقني"]:
        st.subheader("🛠️ تحديث حالة الإصلاح")
        st.write("هنا يقوم التقني بتأكيد إنهاء العمل.")
        # عرض المهام العالقة فقط
        # (كود التحديث يتطلب ربط API للكتابة في الإكسل)
    else:
        st.warning("هذا القسم مخصص لفريق الصيانة فقط.")
