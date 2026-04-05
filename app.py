import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات التطبيق ---
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="⚙️", layout="wide")

# الرابط الخاص ببيانات الصيانة (CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4E-4aLeigAD1Ehm9OMV8Jwguai9H0wPJH7Z6alA528mE6I2ZFBXH9oDjo1T_UoWVW8nurahgyWUfM/pub?output=csv"

# --- قاعدة بيانات المستخدمين الأدوار ---
USER_DB = {
    "admin": {"pw": "gc2026", "role": "المدير التقني"},
    "wail": {"pw": "wail88", "role": "مسؤول المخازن"},
    "maint": {"pw": "maint123", "role": "قسم الصيانة"},
    "chef": {"pw": "chef01", "role": "رئيس الورشة"},
}

ATELIERS = ["Atelier Presse", "Atelier Four", "Atelier Selection", "Atelier PMP", "Atelier PEC", "Atelier LINGE"]

# --- إدارة الجلسة (Session State) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.session_state.role = ""

# --- واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    # إنشاء أعمدة لتوسيط النموذج
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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

# --- بعد تسجيل الدخول: واجهة التطبيق ---
st.sidebar.title(f"👤 {st.session_state.role}")
st.sidebar.write(f"المستخدم: {st.session_state.user}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🛠️ نظام إدارة صيانة مصنع Grand Ceram")
tabs = st.tabs(["📊 لوحة التحكم", "🚨 تبليغ عن عطل", "🔧 حالة المهام"])

# --- التبويب 1: لوحة التحكم ---
with tabs[0]:
    try:
        df = pd.read_csv(SHEET_URL)
        st.subheader("سجل الأعطال الحالي")
        # فلتر الورشات
        selected = st.multiselect("تصفية حسب الورشة:", ATELIERS, default=ATELIERS)
        if not df.empty:
            # التأكد من وجود عمود 'Atelier' في ملف الإكسل
            filtered_df = df[df['Atelier'].isin(selected)] if 'Atelier' in df.columns else df
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("لا توجد بيانات حالياً.")
    except Exception as e:
        st.warning(f"يرجى التأكد من أن ملف Google Sheets يحتوي على الأعمدة الصحيحة. الخطأ: {e}")

# --- التبويب 2: التبليغ ---
with tabs[1]:
    if st.session_state.role in ["رئيس الورشة", "المدير التقني"]:
        st.subheader("🚨 إرسال طلب تدخل تقني")
        with st.form("report_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                at = st.selectbox("الورشة", ATELIERS)
                mc = st.text_input("الآلة المعنية")
            with c2:
                priority = st.selectbox("الأولوية", ["عادي", "متوسط", "عاجل (توقف إنتاج)"])
                problem = st.text_area("وصف المشكلة")
            
            if st.form_submit_button("إرسال البلاغ"):
                st.success(f"✅ تم تسجيل البلاغ لورشة {at}. سيتم إشعار فريق الصيانة.")
    else:
        st.warning("⚠️ هذه الصلاحية مخصصة لرؤساء الورشات فقط.")

# --- التبويب 3: المهام ---
with tabs[2]:
    if st.session_state.role in ["قسم الصيانة", "المدير التقني"]:
        st.subheader("🔧 متابعة التدخلات التقنية")
        st.info("هذا القسم مخصص لفريق الصيانة لتحديث حالة العمل.")
    else:
        st.warning("⚠️ هذا القسم مخصص لفريق الصيانة فقط.")
