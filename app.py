import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Grand Ceram CMMS Pro", page_icon="⚙️", layout="wide")

# روابط البيانات (CSV) التي أرسلتها
URL_REPORTS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStO5FalGVSBXYzvsCSOJ7CAXaQ1iIZsdSIcYFwnY5j2aQ_1_-QYxHV8kk2NmXKO9q8iCU62q0zZS75/pub?output=csv"
URL_MAINT_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7AM-YQyJE8YFnFaTLn_dBL6qvCWwfszDVxiY_ObNTH6HEdK6vxswWuMW11BfqW4tYJp5w_2teRxp2/pub?output=csv"

# روابط الفومات المدمجة (Embed)
FORM_CHEF = "https://docs.google.com/forms/d/1yiAXME-nXY9Sf5FbFXnKl6cdA7p_GCIm0ZeCRSi_NEI/viewform?embedded=true"
FORM_MAINT = "https://docs.google.com/forms/d/1DZLTyHZUEtBSuqIlfqgXCvvmR_6nv9kHQn5COiVU9Qw/viewform?embedded=true"

# --- 2. قاعدة بيانات المستخدمين ---
USER_DB = {
    "admin": {"pw": "gc2026", "role": "المدير التقني"},
    "wail": {"pw": "wail88", "role": "مسؤول المخازن"},
    "maint": {"pw": "maint123", "role": "قسم الصيانة"},
    "chef": {"pw": "chef01", "role": "رئيس الورشة"},
}

# --- 3. إدارة الجلسة وتسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔐 دخول نظام Grand Ceram")
        with st.form("login"):
            u = st.text_input("اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                if u in USER_DB and USER_DB[u]["pw"] == p:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u, USER_DB[u]["role"]
                    st.rerun()
                else: st.error("❌ خطأ في اسم المستخدم أو كلمة المرور")
    st.stop()

# --- 4. واجهة التطبيق الرئيسية ---
st.sidebar.title(f"👤 {st.session_state.role}")
st.sidebar.write(f"المستعمل: {st.session_state.user}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🛠️ إدارة صيانة SARL Grand Ceram")
st.divider()

tabs = st.tabs(["📊 المتابعة العامة", "🚨 تبليغ (رئيس ورشة)", "🔧 إغلاق مهمة & طلب قطع"])

# --- التبويب 1: المتابعة (لوحة التحكم) ---
with tabs[0]:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📋 بلاغات الورشة الجارية")
        try:
            df1 = pd.read_csv(URL_REPORTS)
            st.dataframe(df1, use_container_width=True, hide_index=True)
        except: st.info("في انتظار استقبال أول بلاغ عطل...")

    with col_b:
        st.subheader("📦 تقارير الإصلاح وسحب القطع")
        try:
            df2 = pd.read_csv(URL_MAINT_DATA)
            st.dataframe(df2, use_container_width=True, hide_index=True)
        except: st.info("في انتظار تسجيل أول عملية إصلاح...")

    if st.button("🔄 تحديث البيانات الآن"):
        st.cache_data.clear()
        st.rerun()

# --- التبويب 2: تبليغ الورشة ---
with tabs[1]:
    if st.session_state.role in ["رئيس الورشة", "المدير التقني", "مسؤول المخازن"]:
        st.subheader("📝 إرسال بلاغ عطل فوري")
        st.components.v1.iframe(FORM_CHEF, height=800, scrolling=True)
    else:
        st.warning("⚠️ هذه الصلاحية لرؤساء الورشات والإدارة فقط.")

# --- التبويب 3: تقرير التقني ---
with tabs[2]:
    if st.session_state.role in ["قسم الصيانة", "مسؤول المخازن", "المدير التقني"]:
        st.subheader("✅ تأكيد الإصلاح وطلب قطع الغيار")
        st.info("ملاحظة: يمكنك تخطي طلب القطع إذا اخترت 'لا' في السؤال الخاص بها.")
        st.components.v1.iframe(FORM_MAINT, height=800, scrolling=True)
    else:
        st.warning("⚠️ هذا القسم خاص بتقنيي الصيانة ومسؤول المخازن فقط.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Grand Ceram Pro v2.6 - {datetime.now().year}")
