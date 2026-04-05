import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# 1. إعداد الاتصال بجداول بيانات جوجل
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # تأكد من وضع اسم ملف الـ JSON الخاص بك هنا
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    # اسم الملف الذي ظهر في صورك
    sheet = client.open("GrandCeram_Data")
    return sheet

sheet = init_connection()

# 2. واجهة تسجيل الدخول
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🛠️ نظام إدارة الصيانة - Grand Ceram")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    
    if st.button("تسجيل الدخول"):
        users_sheet = sheet.worksheet("Users").get_all_records()
        df_users = pd.DataFrame(users_sheet)
        
        # التحقق من البيانات
        match = df_users[(df_users['Username'] == user) & (df_users['Password'].astype(str) == pw)]
        if not match.empty:
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = match.iloc[0]['Role']
            st.session_state['username'] = user
            st.rerun()
        else:
            st.error("خطأ في بيانات الدخول")

# 3. محتوى التطبيق بعد تسجيل الدخول
else:
    role = st.session_state['user_role']
    st.sidebar.title(f"مرحباً {st.session_state['username']}")
    st.sidebar.write(f"الدور: {role}")
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- واجهة رئيس الورشة ---
    if role == "Chef d'atelier": # تأكد من مطابقة المسمى في Sheet
        st.header("📋 التبليغ عن عطب جديد")
        with st.form("breakdown_form"):
            workshop = st.selectbox("الورشة", ["الورشة 1", "الورشة 2", "الورشة 3"])
            priority = st.select_slider("الأولوية", options=["Low", "Medium", "High"])
            desc = st.text_area("وصف العطب")
            submitted = st.form_submit_button("إرسال الطلب")
            
            if submitted:
                tickets = sheet.worksheet("Sheet1")
                new_id = len(tickets.get_all_values())
                tickets.append_row([new_id, workshop, priority, desc, "Open", str(datetime.now())])
                st.success("تم إرسال الطلب بنجاح!")

    # --- واجهة المانتونونس ---
    elif role == "Maintenance":
        st.header("🔧 مهام الصيانة")
        tickets_ws = sheet.worksheet("Sheet1")
        df_tickets = pd.DataFrame(tickets_ws.get_all_records())
        
        open_tickets = df_tickets[df_tickets['Status'] == 'Open']
        st.subheader("الأعطال المنتظرة")
        st.table(open_tickets)
        
        selected_id = st.number_input("أدخل رقم العطب للبدء فيه", step=1)
        if st.button("قبول المهمة"):
            # تحديث الحالة إلى "In Progress"
            cell = tickets_ws.find(str(selected_id))
            tickets_ws.update_cell(cell.row, 5, "In Progress")
            st.info(f"تم قبول العطب رقم {selected_id}")

    # --- واجهة مسؤول المخازن (أنت) ---
    elif role == "Gestionnaire magasin":
        st.header("📦 طلبات قطع الغيار")
        stock_ws = sheet.worksheet("Stock")
        df_stock = pd.DataFrame(stock_ws.get_all_records())
        st.write("القطع المطلوبة حالياً:")
        st.table(df_stock)
        
        # إضافة منطق تأكيد التسليم هنا

    # --- واجهة المدير التقني ---
    elif role == "Directeur Technique":
        st.header("📊 المتابعة العامة")
        all_tickets = pd.DataFrame(sheet.worksheet("Sheet1").get_all_records())
        st.dataframe(all_tickets)
