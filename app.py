import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

# العنوان
st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# --- معالجة اتصال Google Sheets الذكي ---
@st.cache_resource
def get_connection():
    try:
        # جلب البيانات من Secrets وتحويلها لقاموس
        secret_info = st.secrets["connections"]["gsheets"].to_dict()
        
        # تنظيف المفتاح الخاص (الحل الجذري للخطأ الأحمر)
        if "private_key" in secret_info:
            # استبدال \\n بـ \n الحقيقية ليفهمها نظام التشفير
            secret_info["private_key"] = secret_info["private_key"].replace("\\n", "\n")
        
        # إنشاء الاتصال بالبيانات المجهزة
        return st.connection("gsheets", type=GSheetsConnection, **secret_info)
    except Exception as e:
        st.error(f"⚠️ فشل الاتصال بقاعدة البيانات. تأكد من إعدادات Secrets. الخطأ: {e}")
        st.stop()

conn = get_connection()

# دالة لقراءة البيانات
def load_data():
    try:
        return conn.read(ttl=5).dropna(how="all")
    except:
        return pd.DataFrame()

df = load_data()

# --- القائمة الجانبية (تسجيل بلاغ) ---
st.sidebar.header("📝 تسجيل بلاغ جديد")
with st.sidebar.form(key="maintenance_form", clear_on_submit=True):
    workshop = st.selectbox("الورشة / القسم", ["الفرن (Four)", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    priority = st.select_slider("الأهمية", options=["منخفضة", "متوسطة", "عالية", "عاجلة"])
    description = st.text_area("وصف العطل")
    submit = st.form_submit_button("إرسال البلاغ")

if submit:
    if description:
        new_report = pd.DataFrame([{
            "ID": len(df) + 1,
            "Workshop": workshop,
            "Priority": priority,
            "Description": description,
            "Status": "قيد الانتظار",
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        updated_df = pd.concat([df, new_report], ignore_index=True)
        conn.update(data=updated_df)
        st.sidebar.success("✅ تم التسجيل بنجاح!")
        st.rerun()
    else:
        st.sidebar.warning("⚠️ يرجى وصف العطل.")

# --- عرض البيانات ---
if not df.empty:
    col1, col2 = st.columns(2)
    col1.metric("إجمالي البلاغات", len(df))
    col2.metric("تحت المعالجة", len(df[df['Status'] == 'قيد الانتظار']))
    
    st.subheader("📋 قائمة الطلبات")
    st.dataframe(df.sort_values(by="ID", ascending=False), use_container_width=True)
else:
    st.info("لا توجد بلاغات حالياً.")

st.markdown("---")
st.caption("Grand Ceram v1.1 - تطوير وائل بونيبان")