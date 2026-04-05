import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

# 2. العنوان
st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# --- الحل النهائي لمشكلة التكرار والمفتاح الخاص ---
@st.cache_resource
def get_connection():
    try:
        # جلب البيانات من Secrets وتحويلها لقاموس
        secret_info = st.secrets["connections"]["gsheets"].to_dict()
        
        # تنظيف المفتاح الخاص (استبدال \\n بـ \n الحقيقية)
        if "private_key" in secret_info:
            secret_info["private_key"] = secret_info["private_key"].replace("\\n", "\n")
            
        # إزالة 'type' من القاموس إذا كانت موجودة لتجنب تكرارها مع المتغير في st.connection
        secret_info.pop("type", None)
        
        # إنشاء الاتصال (نمرر gsheets و GSheetsConnection بشكل صريح)
        return st.connection("gsheets", type=GSheetsConnection, **secret_info)
    except Exception as e:
        st.error(f"⚠️ خطأ في الإعدادات: {e}")
        st.stop()

conn = get_connection()

# 3. دالة قراءة البيانات
def load_data():
    try:
        data = conn.read(ttl=5)
        return data.dropna(how="all")
    except:
        return pd.DataFrame()

df = load_data()

# --- القائمة الجانبية ---
st.sidebar.header("📝 تسجيل بلاغ جديد")
with st.sidebar.form(key="maintenance_form", clear_on_submit=True):
    workshop = st.sidebar.selectbox("الورشة / القسم", ["الفرن (Four)", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    priority = st.sidebar.select_slider("الأهمية", options=["منخفضة", "متوسطة", "عالية", "عاجلة"])
    description = st.sidebar.text_area("وصف العطل")
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
        st.success("✅ تم تسجيل البلاغ بنجاح!")
        st.rerun()
    else:
        st.sidebar.warning("⚠️ يرجى كتابة الوصف.")

# --- عرض الإحصائيات والجدول ---
if not df.empty:
    c1, c2 = st.columns(2)
    c1.metric("إجمالي البلاغات", len(df))
    c2.metric("بلاغات قيد الانتظار", len(df[df['Status'] == 'قيد الانتظار']))
    
    st.subheader("📋 قائمة طلبات الصيانة")
    st.dataframe(df.sort_values(by="ID", ascending=False), use_container_width=True)
else:
    st.info("لا توجد بلاغات مسجلة حالياً.")

st.markdown("---")
st.caption("Grand Ceram v1.2 - تطوير وائل بونيبان")