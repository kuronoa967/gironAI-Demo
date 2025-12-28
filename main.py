import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# -------------------------
# Firestore 初期化
# -------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase_admin"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

API_KEY = st.secrets["firebase_auth"]["api_key"]

# -------------------------
# UI
# -------------------------
st.title("Firebase Auth REST API 体験")

email = st.text_input("メールアドレス")
password = st.text_input("パスワード", type="password")

# -------------------------
# 新規登録
# -------------------------
if st.button("新規登録"):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    r = requests.post(url, json=payload)
    data = r.json()

    if "localId" in data:
        st.success("登録成功")
    else:
        st.error(data)

# -------------------------
# ログイン
# -------------------------
if st.button("ログイン"):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    r = requests.post(url, json=payload)
    data = r.json()

    if "localId" in data:
        uid = data["localId"]

        # Firestore に保存
        db.collection("users").document(uid).set({
            "email": email
        })

        st.success("ログイン成功")
        st.write("UID:", uid)
    else:
        st.error(data)
