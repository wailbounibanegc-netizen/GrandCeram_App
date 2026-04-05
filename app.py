import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# إعداد الصفحة وتصميمها
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🏗️", layout="wide")

st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# إنشاء الاتصال - نكتفي بتعريف النوع هنا فقط لمنع التكرار
conn = st.connection("gsheets", type=GSheetsConnection)

# دالة قراءة البيانات (تجنبنا وضع أي Argument داخل read لتفادي خطأ type)
def load_data():
    try:
        # القراءة الخام لمنع التعارض مع إعدادات Secrets
        data = conn.read()
        if data is not None:
            return data.dropna(how="all")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ فشل جلب البيانات: {e}")
        return pd.DataFrame()

df = load_data()

# القائمة الجانبية لإدخال البيانات
st.sidebar.header("📝 تسجيل بلاغ جديد")
with st.sidebar.form(key="maintenance_form", clear_on_submit=True):
    workshop = st.sidebar.selectbox("القسم", ["الفرن", "التحضير", "التوضيب", "المطحنة", "الميكانيك", "الكهرباء"])
    desc = st.sidebar.text_area("وصف العطل")
    priority = st.sidebar.select_slider("الأهمية", options=["منخفضة", "عالية"])
    submit = st.form_submit_button("إرسال البلاغ")

if submit and desc:
    # تجهيز السطر الجديد بناءً على ترتيب أعمدتك في الصورة
    # الترتيب: ID, Workshop, Priority, Description, Status, Date
    new_entry = pd.DataFrame([{
        "ID": len(df) + 1,
        "Workshop": workshop,
        "Priority": priority,
        "Description": desc,
        "Status": "قيد الانتظار",
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }])
    
    try:
        # دمج البيانات وتحديث الجدول
        updated_df = pd.concat([df, new_entry], ignore_index=True)
        conn.update(data=updated_df)
        st.success("✅ تم حفظ البلاغ بنجاح في الجدول!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ فشل التحديث: {e}")

# عرض الجدول الرئيسي
if not df.empty:
    st.subheader("📋 سجل بلاغات الصيانة")
    # عرض الجدول بترتيب تنازلي (الأحدث أولاً)
    st.dataframe(df.sort_values(by="ID", ascending=False), use_container_width=True)
else:
    st.info("لا توجد بلاغات مسجلة حالياً في Sheet1.")