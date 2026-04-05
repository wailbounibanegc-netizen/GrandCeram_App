import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# دالة الاتصال المباشر (الأكثر استقراراً)
@st.cache_resource
def get_gspread_client():
    try:
        s = st.secrets["connections"]["gsheets"]
        
        # بناء الاعتمادات يدوياً لتجنب أي تعارض في الكلمات المحجوزة
        creds_dict = {
            "type": "service_account",
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": s["private_key"], # لا نحتاج replace هنا بسبب الـ """ في Secrets
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # فتح الجدول باستخدام الرابط المباشر
        return client.open_by_url(s["spreadsheet"]).sheet1
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال: {e}")
        st.stop()

sheet = get_gspread_client()

# دالة لقراءة البيانات وتحويلها لـ DataFrame
def load_data():
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

df = load_data()

# واجهة المستخدم (القائمة الجانبية)
st.sidebar.header("📝 تسجيل بلاغ جديد")
with st.sidebar.form(key="maintenance_form", clear_on_submit=True):
    workshop = st.sidebar.selectbox("الورشة / القسم", ["الفرن", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    desc = st.sidebar.text_area("وصف العطل")
    priority = st.sidebar.select_slider("الأهمية", options=["منخفضة", "عالية"])
    submit = st.form_submit_button("إرسال البلاغ")

if submit and desc:
    # إضافة السطر الجديد مباشرة لـ Google Sheets
    # الترتيب: ID, Workshop, Description, Priority, Status, Date
    new_row = [len(df) + 1, workshop, desc, priority, "قيد الانتظار", datetime.now().strftime("%Y-%m-%d %H:%M")]
    try:
        sheet.append_row(new_row)
        st.success("✅ تم تسجيل البلاغ بنجاح!")
        st.rerun()
    except Exception as e:
        st.error(f"فشل الحفظ: {e}")

# عرض البيانات في الصفحة الرئيسية
if not df.empty:
    st.subheader("📋 قائمة طلبات الصيانة")
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد بلاغات مسجلة حالياً.")