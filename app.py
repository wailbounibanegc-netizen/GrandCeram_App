import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

# العنوان الرئيسي
st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown("---")

# الاتصال بجدول بيانات جوجل
conn = st.connection("gsheets", type=GSheetsConnection)

# دالة لقراءة البيانات
def load_data():
    # قراءة البيانات مع تحديث كل 5 ثوانٍ
    return conn.read(ttl=5).dropna(how="all")

try:
    df = load_data()
except Exception as e:
    st.error("خطأ في الاتصال بقاعدة البيانات. تأكد من إعدادات Secrets وصلاحيات الجدول.")
    st.stop()

# --- القائمة الجانبية لإضافة بلاغ جديد ---
st.sidebar.header("📝 تسجيل بلاغ صيانة جديد")
with st.sidebar.form(key="maintenance_form"):
    workshop = st.selectbox("الورشة / القسم", ["الفرن (Four)", "التحضير (Préparation)", "التوضيب (Triage)", "المطحنة (Broyeur)", "أخرى"])
    priority = st.select_slider("درجة الأهمية", options=["منخفضة", "متوسطة", "عالية", "عاجلة"])
    description = st.text_area("وصف العطل / المشكلة")
    submit_button = st.form_submit_button(label="إرسال البلاغ")

if submit_button:
    if description:
        # تجهيز البيانات الجديدة
        new_id = len(df) + 1
        new_report = pd.DataFrame([{
            "ID": new_id,
            "Workshop": workshop,
            "Priority": priority,
            "Description": description,
            "Status": "قيد الانتظار",
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        
        # دمج البيانات وتحديث الجدول
        updated_df = pd.concat([df, new_report], ignore_index=True)
        conn.update(data=updated_df)
        st.sidebar.success("تم تسجيل البلاغ بنجاح!")
        st.rerun()
    else:
        st.sidebar.warning("يرجى كتابة وصف العطل.")

# --- عرض البيانات الرئيسية ---
col1, col2, col3 = st.columns(3)
col1.metric("إجمالي البلاغات", len(df))
col2.metric("بلاغات قيد الانتظار", len(df[df['Status'] == 'قيد الانتظار']))
col3.metric("بلاغات مكتملة", len(df[df['Status'] == 'مكتمل']))

st.subheader("📋 قائمة طلبات الصيانة الحالية")

# تحسين عرض الجدول
st.dataframe(
    df.sort_values(by="ID", ascending=False),
    use_container_width=True,
    column_config={
        "ID": "رقم البلاغ",
        "Workshop": "الورشة",
        "Priority": "الأهمية",
        "Description": "الوصف",
        "Status": "الحالة",
        "Date": "التاريخ"
    }
)

# --- قسم الإحصائيات البسيط ---
st.markdown("---")
st.caption("نظام صيانة Grand Ceram - تم التطوير بواسطة وائل بونيبان")