import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات الصفحة وتحسين العرض للهاتف ---
st.set_page_config(
    page_title="Grand Ceram Pro Mobile", 
    page_icon="⚙️", 
    layout="wide",
    initial_sidebar_state="collapsed" # إخفاء القائمة الجانبية تلقائياً في الهاتف
)

# إضافة التنسيق المخصص للهاتف (CSS)
st.markdown("""
    <style>
    /* جعل الجداول تأخذ عرض الشاشة بالكامل */
    .stDataFrame {
        width: 100% !important;
    }
    /* تحسين مظهر النماذج المدمجة */
    iframe {
        width: 100% !important;
        border: none;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    /* تكبير الأزرار لتسهيل الضغط بالإصبع */
    .stButton button {
        width: 100%;
        height: 3em;
        border-radius: 10px;
        font-weight: bold;
    }
    /* تحسين مظهر التبويبات في الهاتف */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# روابط البيانات (CSV) 
URL_REPORTS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStO5FalGVSBXYzvsCSOJ7CAXaQ1iIZsdSIcYFwnY5j2aQ_1_-QYxHV8kk2NmXKO9q8iCU62q0zZS75/pub?output=csv"
URL_MAINT_DATA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7AM-YQyJE8YFnFaTLn_dBL6qvCWwfszDVxiY_ObNTH6HEdK6vxswWuMW11BfqW4tYJp5w_2teRxp2/pub?output=csv"

# روابط الفومات المدمجة
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
    c1, c2, c3 = st.columns([0.1, 0.8, 0.1])
    with c2:
        st.markdown("<h2 style='text-align: center;'>🔐 Grand Ceram Mobile</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول"):
                if u in USER_DB and USER_DB[u]["pw"] == p:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u, USER_DB[u]["role"]
                    st.rerun()
                else: st.error("❌ خطأ في البيانات")
    st.stop()

# --- 4. واجهة التطبيق الرئيسية ---
st.sidebar.title(f"👤 {st.session_state.role}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.markdown(f"### 🛠️ نظام إدارة الصيانة - {st.session_state.role}")

tabs = st.tabs(["📊 المتابعة", "🚨 تبليغ", "🔧 إغلاق & قطع"])

# التبويب 1: المتابعة
with tabs[0]:
    st.subheader("📋 البلاغات الجارية")
    try:
        df1 = pd.read_csv(URL_REPORTS)
        st.dataframe(df1, use_container_width=True, hide_index=True)
    except: st.info("بانتظار بلاغات...")
    
    st.divider()
    
    st.subheader("📦 تقارير الإصلاح")
    try:
        df2 = pd.read_csv(URL_MAINT_DATA)
        st.dataframe(df2, use_container_width=True, hide_index=True)
    except: st.info("لم تسجل تقارير بعد.")
    
    if st.button("🔄 تحديث"):
        st.cache_data.clear()
        st.rerun()

# التبويب 2: تبليغ الورشة
with tabs[1]:
    if st.session_state.role in ["رئيس الورشة", "المدير التقني", "مسؤول المخازن"]:
        st.components.v1.iframe(FORM_CHEF, height=1000, scrolling=True)
    else:
        st.warning("⚠️ مخصص لرؤساء الورشات.")

# التبويب 3: تقرير التقني
with tabs[2]:
    if st.session_state.role in ["قسم الصيانة", "مسؤول المخازن", "المدير التقني"]:
        st.components.v1.iframe(FORM_MAINT, height=1000, scrolling=True)
    else:
        st.warning("⚠️ مخصص لقسم الصيانة.")

st.sidebar.caption(f"Grand Ceram Pro v2.7 - {datetime.now().year}")
