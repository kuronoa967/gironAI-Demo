import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

firebase_config = dict(st.secrets["firebase_auth"])
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase_admin"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("Firebase Auth → Firestore 体験")

email = st.text_input("メールアドレス")
password = st.text_input("パスワード", type="password")

# 新規登録
if st.button("新規登録"):
    user = auth.create_user_with_email_and_password(email, password)
    st.success("登録完了")

# ログイン
if st.button("ログイン"):
    user = auth.sign_in_with_email_and_password(email, password)

    uid = user["localId"]
    user_email = user["email"]

    # Firestoreに保存
    db.collection("users").document(uid).set({
        "email": user_email
    })

    st.success("ログイン成功")
    st.write("UID:", uid)
