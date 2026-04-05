import streamlit as st
from st_gsheets_connection import GSheetsConnectionimport pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="Grand Ceram Inventory Control",
    page_icon="🏗️",
    layout="wide"
)

# --- واجهة المستخدم الرسومية (العنوان) ---
st.title("🏗️ نظام إدارة المخزون - SARL Grand Ceram")
st.markdown("---")

# --- دالة الاتصال الآمن بـ Google Sheets ---
def connect_to_sheet():
    try:
        # استخراج البيانات من Secrets
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        
        # تصحيح تلقائي لمشكلة الرموز في المفتاح الخاص (Private Key)
        if "private_key" in secrets_dict:
            secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")
        
        # إنشاء الاتصال
        conn = st.connection("gsheets", type=GSheetsConnection, **secrets_dict)
        return conn
    except Exception as e:
        st.error(f"⚠️ خطأ في إعدادات الاتصال: {e}")
        return None

conn = connect_to_sheet()

# --- القائمة الجانبية (Navigation) ---
menu = ["عرض المخزون", "إضافة مادة جديدة", "البحث والتصفية"]
choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

if conn:
    if choice == "عرض المخزون":
        st.subheader("📊 جدول البيانات الحالي")
        try:
            # قراءة البيانات من ورقة العمل الأولى
            df = conn.read(ttl="10m") # تحديث البيانات كل 10 دقائق
            st.dataframe(df, use_container_width=True)
            
            if st.button("تحديث البيانات الآن 🔄"):
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.error(f"تعذر قراءة البيانات: {e}")

    elif choice == "إضافة مادة جديدة":
        st.subheader("📥 إضافة مادة جديدة للمخزن")
        
        # نموذج الإدخال
        with st.form(key="add_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("اسم المادة")
                category = st.selectbox("الصنف", ["قطع غيار", "مواد أولية", "أدوات", "أخرى"])
            with col2:
                quantity = st.number_input("الكمية", min_value=0)
                unit = st.text_input("الوحدة (كغ، قطعة، ملم)")
            
            notes = st.text_area("ملاحظات إضافية")
            submit_button = st.form_submit_button(label="حفظ في قاعدة البيانات")

        if submit_button:
            if item_name:
                # هنا يتم تجهيز البيانات للإرسال
                new_data = pd.DataFrame([{
                    "اسم المادة": item_name,
                    "الصنف": category,
                    "الكمية": quantity,
                    "الوحدة": unit,
                    "ملاحظات": notes
                }])
                
                # إلحاق البيانات بالجدول (Append)
                try:
                    # ملاحظة: يجب أن تكون أعمدة الشيت مطابقة تماماً لهذه الأسماء
                    existing_data = conn.read()
                    updated_df = pd.concat([existing_data, new_data], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success(f"✅ تم إضافة {item_name} بنجاح!")
                except Exception as e:
                    st.error(f"فشلت عملية الحفظ: {e}")
            else:
                st.warning("يرجى إدخال اسم المادة على الأقل.")

    elif choice == "البحث والتصفية":
        st.subheader("🔍 البحث السريع عن القطع")
        search_term = st.text_input("ادخل اسم المادة أو الكود...")
        
        if search_term:
            df = conn.read()
            # بحث مرن (غير حساس لحالة الأحرف)
            results = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
            
            if not results.empty:
                st.write(f"تم العثور على {len(results)} نتيجة:")
                st.table(results)
            else:
                st.info("لا توجد نتائج مطابقة لبحثك.")

else:
    st.info("💡 بانتظار إعداد مفاتيح الاتصال في لوحة Secrets...")
