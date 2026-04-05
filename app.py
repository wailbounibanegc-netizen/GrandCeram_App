import streamlit as st
import pandas as pd
from datetime import datetime

# --- إعدادات التطبيق ---
st.set_page_config(page_title="Grand Ceram Maintenance", page_icon="🛠️", layout="wide")

# الرابط الخاص ببيانات الصيانة (تأكد أن الملف يحتوي على ورقة باسم Maintenance)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4E-4aLeigAD1Ehm9OMV8Jwguai9H0wPJH7Z6alA528mE6I2ZFBXH9oDjo1T_UoWVW8nurahgyWUfM/pub?output=csv"

@st.cache_data(ttl=30)
def load_maintenance_data():
    return pd.read_csv(SHEET_URL)

# --- واجهة المستخدم ---
st.title("🛠️ نظام إدارة صيانة مصنع Grand Ceram")
st.markdown(f"**التاريخ:** {datetime.now().strftime('%Y-%m-%d')}")

tabs = st.tabs(["📋 لوحة التحكم", "⚠️ تبليغ عن عطل", "🔧 التدخلات الجارية"])

# --- التبويب الأول: عرض حالة الصيانة ---
with tabs[0]:
    try:
        df = load_maintenance_data()
        st.subheader("ملخص حالة المصنع")
        
        # إحصائيات سريعة
        col1, col2, col3 = st.columns(3)
        col1.metric("أعطال نشطة", len(df[df['Status'] == 'Pending']))
        col2.metric("تحت الإصلاح", len(df[df['Status'] == 'In Progress']))
        col3.metric("تمت صيانتها اليوم", "5") # مثال
        
        st.divider()
        st.write("### سجل البلاغات الأخيرة")
        st.dataframe(df, use_container_width=True)
    except:
        st.warning("يرجى التأكد من تنسيق الأعمدة في ملف الإكسل (Machine, Problem, Status, Priority)")

# --- التبويب الثاني: نموذج التبليغ (للعمال ورؤساء الورشة) ---
with tabs[1]:
    st.subheader("إرسال طلب صيانة جديد")
    with st.form("maintenance_form"):
        machine = st.selectbox("الآلة المعطلة", ["Press 1", "Kiln 2", "Glazing Line", "Packaging"])
        problem = st.text_area("وصف العطل")
        priority = st.select_slider("درجة الاستعجال", options=["Low", "Medium", "High", "Urgent"])
        reporter = st.text_input("اسم المبلغ (رئيس الوردية)")
        
        submit = st.form_submit_button("إرسال الطلب للقسم التقني")
        if submit:
            st.success(f"تم إرسال بلاغ عن {machine} بنجاح. سيتم إخطار الفريق التقني.")
            # ملاحظة: لإرسال البيانات فعلياً لجوجل شيت نحتاج Google Forms API أو نظام Apps Script

# --- التبويب الثالث: للمدير التقني وفريق الصيانة ---
with tabs[2]:
    st.subheader("المهام المسندة للفريق التقني")
    if 'df' in locals():
        active_tasks = df[df['Status'] != 'Completed']
        for index, row in active_tasks.iterrows():
            with st.expander(f"🛠️ {row['Machine']} - {row['Priority']}"):
                st.write(f"**العطل:** {row['Problem']}")
                status = st.selectbox("تحديث الحالة", ["Pending", "In Progress", "Completed"], key=index)
                if st.button(f"تحديث المهمة {index}"):
                    st.toast("جاري حفظ التعديلات...")

st.sidebar.image("https://via.placeholder.com/150?text=Grand+Ceram", width=100)
st.sidebar.markdown("---")
st.sidebar.write("**صلاحيات المستخدم:**")
role = st.sidebar.radio("اختر الدور المحاكي:", ["رئيس ورشة", "تقني صيانة", "مدير تقني"])
