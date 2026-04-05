import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Grand Ceram Pro", page_icon="🏢")

# --- روابط الملفات (استبدل الروابط بالروابط التي نسختها من الخطوة السابقة) ---
# ملاحظة: يجب نشر كل ورقة (Sheet) على حدة كـ CSV أو نشر الملف كامل وتحديده
USERS_URL = "ضع_رابط_csv_الخاص_بورقة_المستخدمين_هنا"
STOCK_URL = "ضع_رابط_csv_الخاص_بورقة_المخزن_هنا"

@st.cache_data(ttl=600) # تحديث البيانات كل 10 دقائق
def load_data(url):
    return pd.read_csv(url)

try:
    users_df = load_data(USERS_URL)
    stock_df = load_data(STOCK_URL)
except Exception as e:
    st.error("يرجى التأكد من نشر الملف كـ CSV على الويب")
    st.stop()

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏢 نظام إدارة Grand Ceram")
    with st.form("login"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            # التحقق من البيانات
            user_match = users_df[(users_df['username'].astype(str) == u) & 
                                  (users_df['password'].astype(str) == str(p))]
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.role = user_match.iloc[0]['role']
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
else:
    st.title("📦 لوحة تحكم المخازن")
    st.dataframe(stock_df)
    if st.button("خروج"):
        st.session_state.logged_in = False
        st.rerun()
