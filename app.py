import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ: {datetime.now().strftime('%Y-%m-%d')}**")
st.markdown("---")

# 2. دالة الاتصال (تجهيز الهوية الرقمية فقط)
@st.cache_resource
def get_db_connection():
    try:
        # جلب البيانات من Secrets
        s = st.secrets["connections"]["gsheets"]
        
        # بناء قاموس الهوية (نضع فيه فقط ما تحتاجه جوجل للتعرف عليك)
        # لاحظ أننا لا نضع 'spreadsheet' هنا لتجنب تكرار الوسائط
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
        
        # إنشاء الاتصال بالهوية المحددة
        return st.connection("gsheets", type=GSheetsConnection, **creds_dict), s["spreadsheet"]
    except Exception as e:
        st.error(f"❌ خطأ في إعدادات الوصول: {e}")
        st.stop()

# تفعيل الاتصال وحفظ رابط الجدول
conn, sheet_url = get_db_connection()

# 3. دالة القراءة (نمرر الرابط فقط لضمان عدم حدوث تداخل مع pandas)
def load_data():
    try:
        # هنا نستخدم الرابط فقط، والمكتبة ستستخدم الهوية التي عرفناها سابقاً تلقائياً
        return conn.read(spreadsheet=sheet_url, ttl=5).dropna(how="all")
    except Exception as e:
        st.warning(f"⚠️ لم يتم العثور على بيانات أو الرابط غير صحيح: {e}")
        return pd.DataFrame()

df = load_data()

# 4. واجهة إدخال البيانات (Sidebar)
st.sidebar.header("📝 تسجيل بلاغ صيانة")
with st.sidebar.form(key="maintenance_entry", clear_on_submit=True):
    workshop = st.selectbox("الورشة / القسم", ["الفرن", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    description = st.text_area("وصف العطل بالتفصيل")
    priority = st.select_slider("درجة الأهمية", options=["منخفضة", "متوسطة", "عالية", "عاجلة"])
    submit_button = st.form_submit_button("إرسال البلاغ")

if submit_button:
    if description:
        # تجهيز السطر الجديد
        new_row = pd.DataFrame([{
            "ID": len(df) + 1,
            "Workshop": workshop,
            "Description": description,
            "Priority": priority,
            "Status": "قيد الانتظار",
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        
        # دمج وتحديث الجدول في Google Sheets
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(spreadsheet=sheet_url, data=updated_df)
        st.success("✅ تم تسجيل البلاغ في قاعدة البيانات!")
        st.rerun()
    else:
        st.sidebar.error("⚠️ يرجى كتابة وصف العطل.")

# 5. عرض البيانات بشكل احترافي
if not df.empty:
    st.subheader("📋 سجل البلاغات الحالية")
    # عرض الجدول مع ترتيب الأحدث أولاً
    st.dataframe(df.sort_values(by="ID", ascending=False), use_container_width=True)
else:
    st.info("لا توجد بلاغات مسجلة حالياً في مصنع جراند سيرام.")

st.markdown("---")
st.caption("نظام إدارة الصيانة - Grand Ceram v1.3")