import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Grand Ceram Maintenance", layout="wide")

# الربط بجدول جوجل
conn = st.connection("gsheets", type=GSheetsConnection)

# قراءة البيانات
df = conn.read(worksheet="Sheet1", ttl=5).dropna(how="all")

st.markdown("<h1 style='text-align: center;'>🏗️ نظام صيانة جراند سيرام (أونلاين)</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 بلاغ جديد")
    with st.form("main_form", clear_on_submit=True):
        workshop = st.selectbox("الورشة", ["FOUR", "SELECTION", "BMR", "PRESSE", "PMP", "PEC"])
        priority = st.select_slider("الأولوية", options=["عادي", "متوسط", "عاجل"])
        desc = st.text_area("وصف العطب")
        if st.form_submit_button("إرسال"):
            new_data = pd.DataFrame([{"ID": len(df)+1, "Workshop": workshop, "Priority": priority, "Description": desc, "Status": "قيد الانتظار", "Date": datetime.now().strftime("%Y-%m-%d %H:%M")}])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("تم الإرسال بنجاح!")
            st.rerun()

with col2:
    st.subheader("📊 السجل المباشر")
    st.dataframe(df, use_container_width=True, hide_index=True)