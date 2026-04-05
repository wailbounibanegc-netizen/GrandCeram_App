import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ: {datetime.now().strftime('%Y-%m-%d')}**")
st.markdown("---")

# --- دالة الاتصال المباشر (تتجاوز مشاكل st.connection) ---
@st.cache_resource
def get_gspread_client():
    try:
        s = st.secrets["connections"]["gsheets"]
        
        # تحديد الصلاحيات المطلوبة
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # بناء الاعتمادات يدوياً لتجنب خطأ "multiple values for type"
        creds_dict = {
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
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # فتح الملف باستخدام الرابط الموجود في Secrets
        sheet = client.open_by_url(s["spreadsheet"]).sheet1
        return sheet
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال المباشر: {e}")
        st.stop()

sheet = get_gspread_client()

# دالة القراءة
def load_data():
    try:
        # جلب جميع البيانات وتحويلها لـ DataFrame
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

df = load_data()

# --- واجهة الإدخال ---
st.sidebar.header("📝 تسجيل بلاغ جديد")
with st.sidebar.form(key="m_form", clear_on_submit=True):
    workshop = st.sidebar.selectbox("القسم", ["الفرن", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    desc = st.sidebar.text_area("وصف العطل")
    priority = st.sidebar.select_slider("الأهمية", options=["منخفضة", "عالية"])
    submit = st.form_submit_button("إرسال البلاغ")

if submit and desc:
    # إضافة السطر الجديد مباشرة للجدول
    new_row = [len(df) + 1, workshop, desc, priority, "قيد الانتظار", datetime.now().strftime("%Y-%m-%d %H:%M")]
    try:
        sheet.append_row(new_row)
        st.success("✅ تم الحفظ بنجاح!")
        st.rerun()
    except Exception as e:
        st.error(f"فشل الإرسال: {e}")

# عرض البيانات
if not df.empty:
    st.subheader("📋 سجل الصيانة")
    st.dataframe(df, use_container_width=True)
else:
    st.info("لا توجد بيانات حالياً.")

    st.markdown("---")

st.caption("نظام إدارة الصيانة - Grand Ceram v1.3")