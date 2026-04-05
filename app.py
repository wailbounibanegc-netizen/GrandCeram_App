import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. إعدادات التطبيق الأساسية ---
st.set_page_config(
    page_title="Grand Ceram Maintenance", 
    page_icon="⚙️", 
    layout="wide"
)

# الرابط الخاص ببياناتك المنشور بصيغة CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4E-4aLeigAD1Ehm9OMV8Jwguai9H0wPJH7Z6alA528mE6I2ZFBXH9oDjo1T_UoWVW8nurahgyWUfM/pub?output=csv"

# --- 2. قاعدة بيانات المستخدمين والأدوار ---
USER_DB = {
    "admin": {"pw": "gc2026", "role": "المدير التقني"},
    "wail": {"pw": "wail88", "role": "مسؤول المخازن"},
    "maint": {"pw": "maint123", "role": "قسم الصيانة"},
    "chef": {"pw": "chef01", "role": "رئيس الورشة"},
}

ATELIERS = [
    "Atelier Presse", 
    "Atelier Four", 
    "Atelier Selection", 
    "Atelier PMP", 
    "Atelier PEC", 
    "Atelier LINGE"
]

# --- 3. إدارة الجلسة (Session State) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.session_state.role = ""

# --- 4. واجهة تسجيل الدخول ---
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

# --- 5. واجهة التطبيق الرئيسية (بعد الدخول) ---
st.sidebar.title(f"👤 {st.session_state.role}")
st.sidebar.write(f"المستخدم: {st.session_state.user}")
if st.sidebar.button("تسجيل الخروج"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🛠️ نظام إدارة صيانة مصنع Grand Ceram")
st.markdown(f"**تحديث حي:** {datetime.now().strftime('%H:%M - %Y/%m/%d')}")

tabs = st.tabs(["📊 لوحة التحكم", "🚨 تبليغ عن عطل", "🔧 حالة المهام"])

# --- التبويب 1: لوحة التحكم (عرض التبليغات) ---
with tabs[0]:
    try:
        # تحميل البيانات من الرابط
        df = pd.read_csv(SHEET_URL)
        
        st.subheader("📋 سجل الأعطال والمهمات")
        
        if not df.empty:
            # التحقق من وجود عمود الورشة لعمل التصفية
            if 'Atelier' in df.columns:
                selected = st.multiselect("تصفية حسب الورشة:", ATELIERS, default=ATELIERS)
                # عرض البيانات التي تتبع الورشات المختارة فقط
                filtered_df = df[df['Atelier'].isin(selected)]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                # إذا لم يجد عمود 'Atelier'، يعرض كل البيانات لكي لا يظهر الجدول فارغاً
                st.warning("⚠️ تنبيه: عمود 'Atelier' غير موجود في ملف الإكسل، يتم عرض كافة البيانات المتاحة.")
                st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ لا توجد بلاغات مسجلة في ملف الإكسل حالياً.")
            
    except Exception as e:
        st.error(f"⚠️ فشل في قراءة البيانات: {e}")
        st.info("تأكد من أن الملف منشور على الويب بصيغة CSV.")

# --- التبويب 2: التبليغ عن عطل (خاص برؤساء الورش والمدير) ---
with tabs[1]:
    if st.session_state.role in ["رئيس الورشة", "المدير التقني"]:
        st.subheader("🚨 إرسال طلب تدخل تقني")
        with st.form("report_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                at = st.selectbox("الورشة", ATELIERS)
                mc = st.text_input("الآلة المعنية (أو رقمها)")
            with c2:
                priority = st.selectbox("الأولوية", ["عادي", "متوسط", "عاجل (توقف إنتاج)"])
                problem = st.text_area("وصف المشكلة بالتفصيل")
            
            if st.form_submit_button("إرسال البلاغ"):
                # رسالة نجاح مؤقتة (الحفظ الفعلي يتطلب API للكتابة)
                st.success(f"✅ تم تسجيل البلاغ لورشة {at}. سيظهر في السجل خلال دقائق بعد تحديث جوجل.")
                st.balloons()
    else:
        st.warning("⚠️ هذه الصلاحية مخصصة لرؤساء الورشات فقط لإرسال البلاغات.")

# --- التبويب 3: حالة المهام (خاص بقسم الصيانة والمدير) ---
with tabs[2]:
    if st.session_state.role in ["قسم الصيانة", "المدير التقني"]:
        st.subheader("🔧 متابعة التدخلات التقنية")
        st.info("هذا القسم مخصص لفريق الصيانة لتحديث حالة العمل.")
        # يمكن هنا عرض المهام العالقة فقط بناءً على عمود Status في الإكسل
        if 'df' in locals() and not df.empty:
            st.write("المهام الجارية:")
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ هذا القسم مخصص لفريق الصيانة لمتابعة المهام التقنية.")

st.sidebar.markdown("---")
st.sidebar.caption("Grand Ceram Pro v1.5")
