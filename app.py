import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Grand Ceram Pro", page_icon="📦", layout="centered")

# --- دالة الاتصال بقاعدة البيانات ---
def init_connection():
    try:
        # نأخذ نسخة من Secrets لتجنب خطأ "item assignment"
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # إصلاح تنسيق المفتاح الخاص
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        # النطاقات المطلوبة للوصول لجوجل شيت ودرايف
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # السطر المصحح: استخدام from_json_keyfile_dict بدلاً من from_json_metadata
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # فتح ملف البيانات (تأكد أن الاسم هو GrandCeram_Data في جوجل)
        return client.open("GrandCeram_Data")
    except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال: {e}")
        return None

# تنفيذ الاتصال
sh = init_connection()

if sh:
    try:
        users_sheet = sh.worksheet("Users")
        stock_sheet = sh.worksheet("Stock")
    except Exception as e:
        st.error(f"لم يتم العثور على جداول Users أو Stock: {e}")
        st.stop()
else:
    st.stop()

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏢 نظام إدارة SARL Grand Ceram")
    st.subheader("تسجيل الدخول - المخازن والتموين")
    
    with st.form("login_form"):
        user_input = st.text_input("اسم المستخدم")
        pass_input = st.text_input("كلمة المرور", type="password")
        submit_button = st.form_submit_button("دخول")
        
        if submit_button:
            users_df = pd.DataFrame(users_sheet.get_all_records())
            user_match = users_df[(users_df['username'] == user_input) & (users_df['password'] == str(pass_input))]
            
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = user_input
                st.session_state.user_role = user_match.iloc[0]['role']
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
else:
    st.sidebar.success(f"مرحباً: {st.session_state.user_name}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    st.header("📦 حالة المخزون الحالي")
    stock_df = pd.DataFrame(stock_sheet.get_all_records())
    st.dataframe(stock_df, use_container_width=True)
