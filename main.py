import streamlit as st
from streamlit_option_menu import option_menu
import requests
import firebase_admin
from firebase_admin import credentials, firestore

st.markdown(
    """
    <style>
    .st-emotion-cache-1r1cntt {
        padding-bottom: 0rem !important;
    }
    .st-emotion-cache-10p9htt {
        margin-bottom: 0rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase_admin"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

API_KEY = st.secrets["firebase_auth"]["api_key"]

st.set_page_config(layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "chat"   # 通常はチャット画面

if "user" not in st.session_state:
    st.session_state.user = None     # None = 未ログイン

if "chats" not in st.session_state:
    st.session_state.chats = [
        {"id": "chat1", "title": "働き方について"},
        {"id": "chat2", "title": "将来の不安"},
        {"id": "chat3", "title": "AIとの対話"},
    ]

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "force_select_index" not in st.session_state:
    st.session_state.force_select_index = None

def show_account_page():
    # -------------------------
    # 未ログインの場合
    # -------------------------
    if st.session_state.user is None:
        st.title("ログイン / 新規登録")

        email = st.text_input("メールアドレス")
        password = st.text_input("パスワード", type="password")

        col1, col2 = st.columns(2)

        # 新規登録
        with col1:
            if st.button("新規登録"):
                if not email or not password:
                    st.error("メールアドレスとパスワードを入力してください")
                    st.stop()
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

        # ログイン
        with col2:
            if st.button("ログイン"):
                if not email or not password:
                    st.error("メールアドレスとパスワードを入力してください")
                    st.stop()
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

                    # Firestore に保存（初回 or 上書き）
                    db.collection("users").document(uid).set({
                        "email": email
                    }, merge=True)

                    # ★ ログイン状態を保存
                    st.session_state.user = {
                        "uid": uid,
                        "email": email
                    }

                    st.success("ログイン成功")
                    st.session_state.page = "chat"
                    st.rerun()
                else:
                    st.error(data)

    # -------------------------
    # ログイン済みの場合
    # -------------------------
    else:
        st.title("アカウント")

        st.write("メールアドレス:")
        st.code(st.session_state.user["email"])

        if st.button("ログアウト", type="primary"):
            st.session_state.user = None
            st.session_state.page = "chat"
            st.success("ログアウトしました")
            show_chat_page()

def show_chat_page():
    st.write(st.session_state.page)
    st.write(st.session_state.user)
    prompt = st.chat_input("議題を入力してください…")

def on_change(key):
    selection = st.session_state[key]
    st.write(f"Selection changed to {selection}")

with st.sidebar:
    # ① 一番上：新規チャット
    if st.button("新規チャット", use_container_width=True):
        new_id = f"chat{len(st.session_state.chats) + 1}"
        st.session_state.chats.append(
            {"id": new_id, "title": "新しいチャット"}
        )
        st.session_state.current_chat_id = new_id
        st.session_state.force_select_index = len(st.session_state.chats) - 1
        st.session_state.page = "chat"
        st.rerun()

    # ② 真ん中：チャット一覧
    if st.session_state.user is None:
        # 未ログイン時
        st.markdown(
            """
            <div style="
                padding: 1rem;
                color: #888;
                font-size: 0.9rem;
                text-align: center;
            ">
                ログインすると<br>
                チャット履歴が保存されます
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        chat_titles = [c["title"] for c in st.session_state.chats]
        chat_id_map = {c["title"]: c["id"] for c in st.session_state.chats}

        manual_select = None
        if st.session_state.force_select_index is not None:
            manual_select = st.session_state.force_select_index
        
        selected_chat = option_menu(
            menu_title=None,
            options=chat_titles,
            icons=[None] * len(chat_titles),
            on_change=on_change,
            key='menu_5',
            manual_select=manual_select,
            styles={
                "container": {
                    "max-height": "400px",
                    "height": "400px",
                    "overflow-y": "auto",
                },
                "icon": {
                    "display": "none",
                    "margin-right": "0",
                    "width": "0",
                },
                "nav": {
                    "font-size": "14px",
                },
            },
        )

        if st.session_state.force_select_index is not None:
            st.session_state.force_select_index = None

    # ③ 一番下：アカウントボタン
    if st.button("アカウント", use_container_width=True):
        st.session_state.page = "account"

if st.session_state.page == "chat":
    show_chat_page()

elif st.session_state.page == "account":
    show_account_page()
