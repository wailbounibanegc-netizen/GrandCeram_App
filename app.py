import streamlit as st
import pandas as pd

# --- إعدادات الصفحة لمصنع Grand Ceram ---
st.set_page_config(
    page_title="Grand Ceram Pro",
    page_icon="🏢",
    layout="wide"
)

# الرابط الخاص بك بصيغة CSV (الذي أرسلته أنت)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR4E-4aLeigAD1Ehm9OMV8Jwguai9H0wPJH7Z6alA528mE6I2ZFBXH9oDjo1T_UoWVW8nurahgyWUfM/pub?output=csv"

# دالة لجلب البيانات مع ذاكرة مؤقتة لتسريع التطبيق
@st.cache_data(ttl=60)
def load_data():
    try:
        # قراءة البيانات مباشرة من الرابط
        return pd.read_csv(SHEET_URL)
    except Exception as e:
        st.error(f"⚠️ خطأ في قراءة البيانات: {e}")
        return None

# --- واجهة التطبيق ---
st.title("🏢 نظام إدارة المخازن - SARL Grand Ceram")
st.markdown(f"**المسؤول:** {st.session_state.get('user_name', 'وائل')}")
st.divider()

# جلب البيانات
df = load_data()

if df is not None:
    # عرض إحصائيات سريعة في الأعلى
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي المواد", len(df))
    
    st.subheader("📦 جدول المخزون الحالي")
    
    # إضافة شريط بحث
    search = st.text_input("🔍 ابحث عن قطعة غيار أو مادة...")
    if search:
        # البحث في جميع الأعمدة
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

    # عرض الجدول بشكل احترافي
    st.dataframe(df, use_container_width=True)
    
    # زر للتحديث اليدوي
    if st.button("🔄 تحديث البيانات الآن"):
        st.cache_data.clear()
        st.rerun()

else:
    st.warning("لم يتم العثور على بيانات. تأكد من أن ملف Google Sheets يحتوي على بيانات وأن الرابط لا يزال صالحاً.")

st.divider()
st.caption("تطوير قسم التموين والمخازن - Grand Ceram Pro v1.0")
