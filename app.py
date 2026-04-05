import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Grand Ceram Maintenance", 
    page_icon="🏗️", 
    layout="wide"
)

# 2. العنوان والتنسيق العلوي
st.title("🏗️ نظام إدارة صيانة جراند سيرام | Grand Ceram")
st.markdown(f"**التاريخ الحالي:** {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# 3. الاتصال بـ Google Sheets (سيسحب البيانات تلقائياً من Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# دالة لتحديث البيانات من الجدول
def load_data():
    try:
        # قراءة البيانات وتجاهل الأسطر الفارغة تماماً
        return conn.read(ttl=5).dropna(how="all")
    except Exception as e:
        st.error(f"خطأ في قراءة البيانات: {e}")
        return pd.DataFrame()

df = load_data()

# --- القائمة الجانبية (إضافة بلاغ جديد) ---
st.sidebar.header("📝 تسجيل بلاغ جديد")
with st.sidebar.form(key="maintenance_form", clear_on_submit=True):
    workshop = st.selectbox(
        "الورشة / القسم", 
        ["الفرن (Four)", "التحضير (Préparation)", "التوضيب (Triage)", "المطحنة (Broyeur)", "الميكانيك", "الكهرباء", "أخرى"]
    )
    priority = st.select_slider(
        "درجة الأهمية", 
        options=["منخفضة", "متوسطة", "عالية", "عاجلة"]
    )
    description = st.text_area("وصف العطل بالتفصيل")
    
    submit_button = st.form_submit_button(label="إرسال البلاغ إلى القاعدة")

if submit_button:
    if description:
        # تجهيز السطر الجديد
        new_id = len(df) + 1
        new_report = pd.DataFrame([{
            "ID": new_id,
            "Workshop": workshop,
            "Priority": priority,
            "Description": description,
            "Status": "قيد الانتظار",
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        
        # دمج البيانات الجديدة مع القديمة
        updated_df = pd.concat([df, new_report], ignore_index=True)
        
        try:
            # تحديث جدول جوجل
            conn.update(data=updated_df)
            st.sidebar.success("✅ تم تسجيل البلاغ بنجاح في Google Sheets!")
            st.rerun() # إعادة تحميل الصفحة لتحديث الجدول
        except Exception as e:
            st.sidebar.error(f"فشل الإرسال: تأكد من مشاركة الجدول مع إيميل الخدمة. الخطأ: {e}")
    else:
        st.sidebar.warning("⚠️ يرجى كتابة وصف العطل قبل الإرسال.")

# --- عرض الإحصائيات السريعة ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي البلاغات", len(df))
    col2.metric("بلاغات قيد الانتظار", len(df[df['Status'] == 'قيد الانتظار']))
    col3.metric("بلاغات مكتملة", len(df[df['Status'] == 'مكتمل']))

st.subheader("📋 قائمة طلبات الصيانة الحالية")

# عرض الجدول بشكل تفاعلي ومنظم
if not df.empty:
    st.dataframe(
        df.sort_values(by="ID", ascending=False), # عرض الأحدث أولاً
        use_container_width=True,
        column_config={
            "ID": "رقم",
            "Workshop": "الورشة",
            "Priority": "الأهمية",
            "Description": "وصف العطل",
            "Status": "الحالة",
            "Date": "التاريخ والوقت"
        }
    )
else:
    st.info("لا توجد بلاغات مسجلة حتى الآن. ابدأ بإضافة بلاغ من القائمة الجانبية.")

# --- التذييل ---
st.markdown("---")
st.caption("نظام صيانة Grand Ceram v1.0 | مطور بواسطة وائل بونيبان")