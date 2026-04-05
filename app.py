import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# --- دالة الاتصال النهائية (بدون تمرير **kwargs لتجنب التعارض) ---
@st.cache_resource
def manual_connect():
    try:
        # جلب البيانات من القسم الصحيح في Secrets
        s = st.secrets["connections"]["gsheets"]
        
        # بناء هيكل الاعتمادات يدوياً لتجنب خطأ "Multiple Values" أو "Unexpected Argument"
        credentials = {
            "type": "service_account",
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": s["private_key"].replace("\\n", "\n"),
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        # إنشاء الاتصال (نمرر فقط النوع، والبيانات نستخدمها داخل الدالة)
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn, credentials, s["spreadsheet"]
    except Exception as e:
        st.error(f"❌ خطأ في قراءة Secrets: {e}")
        st.stop()

conn, creds, sheet_url = manual_connect()

# دالة القراءة المعدلة
def load_data():
    try:
        # نمرر الاعتمادات والرابط في كل عملية قراءة لضمان تخطي الإعدادات التلقائية
        return conn.read(spreadsheet=sheet_url, worksheet="Sheet1", ttl=5, **creds).dropna(how="all")
    except Exception as e:
        st.error(f"خطأ في الوصول للجدول: {e}")
        return pd.DataFrame()

df = load_data()

# --- واجهة الإدخال ---
st.sidebar.header("📝 بلاغ جديد")
with st.sidebar.form("m_form", clear_on_submit=True):
    workshop = st.selectbox("القسم", ["الفرن", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    desc = st.text_area("وصف العطل")
    priority = st.select_slider("الأهمية", options=["منخفضة", "عالية"])
    btn = st.form_submit_button("إرسال")

if btn and desc:
    new_row = pd.DataFrame([{
        "ID": len(df)+1, 
        "Workshop": workshop, 
        "Description": desc, 
        "Status": "قيد الانتظار", 
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    try:
        # التحديث مع تمرير الاعتمادات يدوياً
        conn.update(spreadsheet=sheet_url, data=updated_df, **creds)
        st.success("✅ تم حفظ البلاغ بنجاح!")
        st.rerun()
    except Exception as e:
        st.error(f"فشل التحديث: {e}")

# العرض
if not df.empty:
    st.subheader("📋 سجل الصيانة")
    st.dataframe(df.sort_values(by="ID", ascending=False), use_container_width=True)
else:
    st.info("لا توجد بلاغات مسجلة.")