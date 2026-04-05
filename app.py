import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Grand Ceram Pro", layout="centered")

# --- الاتصال بـ Google Sheets ---
def init_connection():
    # جلب البيانات من Secrets
    creds_dict = st.secrets["connections"]["gsheets"]
    
    # إصلاح تنسيق المفتاح الخاص
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_metadata(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # افتح الملف باسمه الصحيح في جوجل درايف
    return client.open("GrandCeram_Data")

try:
    sh = init_connection()
    users_sheet = sh.worksheet("Users")
    stock_sheet = sh.worksheet("Stock")
except Exception as e:
    st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
    st.stop()

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.header("🏢 نظام إدارة SARL Grand Ceram")
    with st.form("login_form"):
        user_input = st.text_input("اسم المستخدم")
        pass_input = st.text_input("كلمة المرور", type="password")
        submit = st.form_submit_type("دخول")
        
        if submit:
            # التحقق من المستخدمين من الشيت
            users_df = pd.DataFrame(users_sheet.get_all_records())
            user_data = users_df[(users_df['username'] == user_input) & (users_df['password'] == str(pass_input))]
            
            if not user_data.empty:
                st.session_state.logged_in = True
                st.session_state.user_role = user_data.iloc[0]['role']
                st.session_state.user_name = user_input
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
else:
    # --- واجهة التطبيق بعد الدخول ---
    st.sidebar.title(f"مرحباً {st.session_state.user_name}")
    st.sidebar.write(f"الرتبة: {st.session_state.user_role}")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📦 لوحة تحكم المخازن والصيانة")
    
    # عرض المخزون لكل الرتب
    st.subheader("حالة المخزون الحالي")
    stock_data = pd.DataFrame(stock_sheet.get_all_records())
    st.dataframe(stock_data)

    # صلاحيات خاصة لمسؤول المخازن (وائل)
    if st.session_state.user_role in ["Gestionnaire magasin", "Admin"]:
        st.divider()
        st.subheader("إضافة حركة مخزنية")
        with st.expander("تسجيل دخول/خروج قطع غيار"):
            # هنا يمكنك إضافة فورم الإدخال
            st.info("هذا القسم مخصص لك يا وائل لإدارة التوريدات")
