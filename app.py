import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Grand Ceram Pro", layout="centered")

def init_connection():
    try:
        # نسخة من Secrets
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        
        # --- تنظيف المفتاح من أي تشويه في النسخ ---
        raw_key = creds_dict["private_key"]
        # تحويل الرموز وإزالة المسافات الزائدة التي تسبب خطأ Signature
        fixed_key = raw_key.replace("\\n", "\n").strip()
        
        # التأكد من وجود البداية والنهاية الصحيحة للمفتاح
        if "-----BEGIN PRIVATE KEY-----" not in fixed_key:
            fixed_key = "-----BEGIN PRIVATE KEY-----\n" + fixed_key + "\n-----END PRIVATE KEY-----"
            
        creds_dict["private_key"] = fixed_key
        # ---------------------------------------

        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("GrandCeram_Data")
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

sh = init_connection()

if sh:
    try:
        users_sheet = sh.worksheet("Users")
        stock_sheet = sh.worksheet("Stock")
        st.success("✅ متصل بنجاح بقاعدة بيانات Grand Ceram")
    except Exception as e:
        st.error(f"فشل في الوصول للأوراق: {e}")
        st.stop()
    
    # واجهة الدخول البسيطة
    st.title("🏢 نظام إدارة المخازن")
    # (بقية الكود الخاص بك...)
