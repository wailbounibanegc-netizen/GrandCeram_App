import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Grand Ceram Pro", page_icon="📦", layout="centered")

# --- دالة الاتصال بقاعدة البيانات (المصحة) ---
def init_connection():
    try:
        # نأخذ نسخة من Secrets لتجنب خطأ "item assignment"
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # إصلاح تنسيق المفتاح الخاص في النسخة
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_metadata(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # فتح ملف البيانات (تأكد من مطابقة الاسم تماماً في Google Drive)
        return client.open("GrandCeram_Data")
    except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال: {e}")
        return None

# محاولة الاتصال
sh = init_connection()

if sh:
    try:
        users_sheet = sh.worksheet("Users")
        stock_sheet = sh.worksheet("Stock")
    except Exception as e:
        st.error(f"لم يتم العثور على أوراق العمل (Users/Stock): {e}")
        st.stop()
else:
    st.stop()

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏢 نظام إدارة SARL Grand Ceram")
    st.subheader("تسجيل الدخول - قسم التموين والمخازن")
    
    with st.form("login_form"):
        user_input = st.text_input("اسم المستخدم")
        pass_input = st.text_input("كلمة المرور", type="password")
        submit_button = st.form_submit_button("دخول")
        
        if submit_button:
            # جلب بيانات المستخدمين
            users_df = pd.DataFrame(users_sheet.get_all_records())
            
            # التحقق من المطابقة
            user_match = users_df[(users_df['username'] == user_input) & (users_df['password'] == str(pass_input))]
            
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = user_input
                st.session_state.user_role = user_match.iloc[0]['role']
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

else:
    # --- واجهة التطبيق الرئيسية بعد الدخول ---
    st.sidebar.success(f"مرحباً: {st.session_state.user_name}")
    st.sidebar.info(f"الرتبة: {st.session_state.user_role}")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    st.header("📦 لوحة تحكم المخازن")
    
    # عرض جدول المخزون
    st.subheader("حالة قطع الغيار الحالية")
    stock_df = pd.DataFrame(stock_sheet.get_all_records())
    st.dataframe(stock_df, use_container_width=True)

    # قسم خاص بوائل (مسؤول المخازن)
    if st.session_state.user_role == "Gestionnaire magasin":
        st.divider()
        st.subheader("⚙️ أدوات الإدارة")
        st.write("يمكنك إضافة حركات المخزون هنا قريباً.")
