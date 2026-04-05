import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="Grand Ceram Pro",
    page_icon="🏢",
    layout="centered"
)

# --- 2. دالة الاتصال بقاعدة البيانات (المصصحة) ---
def init_connection():
    try:
        # أخذ نسخة من Secrets لتجنب خطأ "item assignment"
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            st.error("لم يتم العثور على إعدادات Connections في Secrets!")
            return None
            
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # معالجة المفتاح الخاص لحل مشكلة التشفير (Base64/JWT)
        raw_key = creds_dict["private_key"]
        creds_dict["private_key"] = raw_key.replace("\\n", "\n").strip()
        
        # النطاقات المطلوبة للوصول
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # الاتصال بجوجل باستخدام الدالة الصحيحة
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # فتح ملف البيانات - تأكد أن الاسم مطابق تماماً في Google Drive
        return client.open("GrandCeram_Data")
    except Exception as e:
        st.error(f"حدث خطأ أثناء الاتصال بقاعدة البيانات: {e}")
        return None

# تنفيذ الاتصال الأولي
sh = init_connection()

# التحقق من وجود أوراق العمل
if sh:
    try:
        users_sheet = sh.worksheet("Users")
        stock_sheet = sh.worksheet("Stock")
    except Exception as e:
        st.error(f"فشل في العثور على 'Users' أو 'Stock' داخل الملف: {e}")
        st.stop()
else:
    st.info("يرجى التأكد من إعدادات Secrets ومشاركة الملف مع إيميل الخدمة.")
    st.stop()

# --- 3. نظام إدارة الجلسة (Session State) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.user_role = ""

# --- 4. واجهة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("🏢 SARL Grand Ceram")
    st.subheader("نظام إدارة المخازن والتموين")
    
    with st.form("login_form"):
        user_input = st.text_input("اسم المستخدم")
        pass_input = st.text_input("كلمة المرور", type="password")
        submit_button = st.form_submit_button("تسجيل الدخول")
        
        if submit_button:
            # جلب بيانات المستخدمين من Google Sheets
            users_df = pd.DataFrame(users_sheet.get_all_records())
            
            # التحقق من المطابقة (username & password)
            user_match = users_df[
                (users_df['username'].astype(str) == user_input) & 
                (users_df['password'].astype(str) == pass_input)
            ]
            
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.user_name = user_input
                st.session_state.user_role = user_match.iloc[0]['role']
                st.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

# --- 5. واجهة التطبيق الرئيسية (بعد الدخول) ---
else:
    # شريط جانبي للمعلومات والخروج
    st.sidebar.title(f"👤 {st.session_state.user_name}")
    st.sidebar.info(f"الرتبة: {st.session_state.user_role}")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📦 لوحة تحكم المخزون")
    
    # عرض جدول المخزون الحالي
    st.subheader("حالة قطع الغيار والمواد")
    try:
        stock_df = pd.DataFrame(stock_sheet.get_all_records())
        st.dataframe(stock_df, use_container_width=True)
    except Exception as e:
        st.error(f"خطأ في عرض البيانات: {e}")

    # ميزات خاصة بوائل (Gestionnaire magasin)
    if st.session_state.user_role == "Gestionnaire magasin":
        st.divider()
        st.subheader("🛠️ أدوات الإدارة")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("إضافة توريد جديد"):
                st.write("سيتم فتح نموذج الإدخال هنا...")
        with col2:
            if st.button("تحديث الكميات"):
                st.write("سيتم فتح نموذج التعديل هنا...")
