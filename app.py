import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# --- معالجة الاتصال والبيانات بنظام "الفلترة" ---
@st.cache_resource
def get_connection():
    try:
        # جلب البيانات من Secrets
        conf = st.secrets["connections"]["gsheets"].to_dict()
        
        # 1. تنظيف المفتاح الخاص (حل مشكلة التشفير)
        if "private_key" in conf:
            conf["private_key"] = conf["private_key"].replace("\\n", "\n")
            
        # 2. حفظ الرابط في متغير منفصل وحذفه من القاموس (حل خطأ الصورة الأخيرة)
        sheet_url = conf.get("spreadsheet")
        
        # حذف الكلمات التي تسبب "unexpected keyword argument"
        keys_to_remove = ["spreadsheet", "type"]
        for key in keys_to_remove:
            conf.pop(key, None)
        
        # 3. إنشاء الاتصال وتمرير الرابط بشكل مستقل
        return st.connection("gsheets", type=GSheetsConnection, **conf), sheet_url
    except Exception as e:
        st.error(f"⚠️ خطأ في الإعدادات: {e}")
        st.stop()

# الحصول على الاتصال والرابط
conn, spreadsheet_url = get_connection()

def load_data():
    try:
        # القراءة باستخدام الرابط الصريح
        return conn.read(spreadsheet=spreadsheet_url, ttl=5).dropna(how="all")
    except Exception as e:
        st.error(f"فشل قراءة البيانات: {e}")
        return pd.DataFrame()

df = load_data()

# --- واجهة الإدخال (القائمة الجانبية) ---
st.sidebar.header("📝 تسجيل بلاغ جديد")
with st.sidebar.form(key="m_form", clear_on_submit=True):
    workshop = st.sidebar.selectbox("الورشة", ["الفرن", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    priority = st.sidebar.select_slider("الأهمية", options=["منخفضة", "متوسطة", "عالية", "عاجلة"])
    description = st.sidebar.text_area("وصف العطل")
    submit = st.form_submit_button("إرسال البلاغ")

if submit and description:
    new_data = pd.DataFrame([{
        "ID": len(df) + 1,
        "Workshop": workshop,
        "Priority": priority,
        "Description": description,
        "Status": "قيد الانتظار",
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }])
    updated_df = pd.concat([df, new_data], ignore_index=True)
    conn.update(spreadsheet=spreadsheet_url, data=updated_df)
    st.success("✅ تم الإرسال!")
    st.rerun()

# --- عرض النتائج ---
if not df.empty:
    st.subheader("📋 البلاغات الحالية")
    st.dataframe(df.sort_values(by="ID", ascending=False), use_container_width=True)
else:
    st.info("لا توجد بيانات حالياً.")