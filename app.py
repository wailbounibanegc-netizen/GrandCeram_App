import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# إعدادات الواجهة
st.set_page_config(page_title="Grand Ceram ERP", page_icon="🏗️", layout="wide")

# الاتصال بجوجل شيت
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0).dropna(how="all")
    except:
        return pd.DataFrame()

# --- نظام الحماية والدخول ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': None, 'role': None})

if not st.session_state.auth:
    st.sidebar.title("🔐 Login / Connexion")
    u = st.sidebar.text_input("Nom d'utilisateur (اسم المستخدم)")
    p = st.sidebar.text_input("Mot de passe (كلمة المرور)", type="password")
    if st.sidebar.button("Se connecter (دخول)"):
        users_df = load_data("Users")
        res = users_df[(users_df['Username'] == u) & (users_df['Password'] == p)]
        if not res.empty:
            st.session_state.update({'auth': True, 'user': u, 'role': res.iloc[0]['Role']})
            st.rerun()
        else:
            st.sidebar.error("Identifiants incorrects / خطأ في الدخول")
    st.stop()

# --- القائمة الجانبية ---
st.sidebar.write(f"👤 **Utilisateur:** {st.session_state.user}")
st.sidebar.write(f"🔑 **Rôle:** {st.session_state.role}")
if st.sidebar.button("Déconnexion (خروج)"):
    st.session_state.auth = False
    st.rerun()

# تحميل البيانات الأساسية
df_maint = load_data("Sheet1")
df_stock = load_data("Stock")

# --- توزيع التبويبات حسب الدور ---
tabs_titles = ["📝 Signalement", "📋 Suivi Maintenance"]

if st.session_state.role in ["Gestionnaire magasin", "Directeur Technique"]:
    tabs_titles.append("📦 Gestion Magasin")
    if st.session_state.role == "Directeur Technique":
        tabs_titles.append("⚙️ Administration")

tabs = st.tabs(tabs_titles)

# 1. تبويب التبليغ (للجميع)
with tabs[0]:
    st.subheader("Signaler une nouvelle panne / تسجيل عطل")
    with st.form("f_panne", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            at = st.selectbox("Atelier (الورشة)", ["Four", "Moulin", "Presse", "Email", "Triage", "Préparation"])
            pr = st.select_slider("Priorité (الأهمية)", ["Basse", "Moyenne", "Haute", "Urgente"])
        with c2:
            ds = st.text_area("Description du problème (وصف العطل)")
        
        if st.form_submit_button("Envoyer (إرسال)"):
            new_p = pd.DataFrame([{
                "ID": len(df_maint) + 1, "Workshop": at, "Priority": pr, 
                "Description": ds, "Status": "En attente", 
                "Date": datetime.now().strftime("%d/%m/%Y %H:%M")
            }])
            conn.update(worksheet="Sheet1", data=pd.concat([df_maint, new_p], ignore_index=True))
            st.success("Signalement envoyé! / تم الإرسال")
            st.rerun()

# 2. تبويب المتابعة (رؤية للكل، تعديل للصيانة والمخزن والمدير)
with tabs[1]:
    st.subheader("Registre de Maintenance / سجل الصيانة")
    st.dataframe(df_maint.sort_values("ID", ascending=False), use_container_width=True)
    
    if st.session_state.role in ["Service Maintenance", "Gestionnaire magasin", "Directeur Technique"]:
        st.divider()
        with st.expander("Update Status / تحديث الحالة"):
            id_ed = st.number_input("ID Panne", min_value=1, step=1)
            n_st = st.selectbox("Statut", ["En cours", "En attente de pièce", "Réparé", "Annulé"])
            if st.button("Mettre à jour"):
                df_maint.loc[df_maint['ID'] == id_ed, 'Status'] = n_st
                conn.update(worksheet="Sheet1", data=df_maint)
                st.rerun()

# 3. تبويب المخزن (خاص بك وبالمسؤول)
if "📦 Gestion Magasin" in tabs_titles:
    with tabs[2]:
        st.subheader("Sortie de Pièces / خروج قطع غيار")
        with st.form("f_stock"):
            id_p = st.number_input("Lier à l'ID Panne", min_value=1)
            itm = st.text_input("Désignation de la pièce")
            qty = st.number_input("Quantité", min_value=1)
            if st.form_submit_button("Enregistrer"):
                new_s = pd.DataFrame([{"ID_Panne": id_p, "Piece_Utilisee": itm, "Quantite": qty, "Date_Sortie": datetime.now().strftime("%d/%m/%Y")}])
                conn.update(worksheet="Stock", data=pd.concat([df_stock, new_s], ignore_index=True))
                st.success("Stock mis à jour!")
                st.rerun()
        st.dataframe(df_stock, use_container_width=True)

# 4. تبويب الإدارة (للمدير التقني فقط)
if "⚙️ Administration" in tabs_titles:
    with tabs[3]:
        st.subheader("Gestion des Utilisateurs / إدارة الحسابات")
        u_df = load_data("Users")
        st.table(u_df[['Username', 'Role']])
        with st.form("f_user"):
            nu = st.text_input("Nouvel Utilisateur")
            np = st.text_input("Mot de passe")
            nr = st.selectbox("Rôle", ["Chef d'Atelier", "Service Maintenance", "Directeur Technique", "Chef de Poste", "Gestionnaire magasin"])
            if st.form_submit_button("Créer Compte"):
                conn.update(worksheet="Users", data=pd.concat([u_df, pd.DataFrame([{"Username": nu, "Password": np, "Role": nr}])]))
                st.rerun()