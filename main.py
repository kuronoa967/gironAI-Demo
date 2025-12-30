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
    st.session_state.chats = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "force_select_index" not in st.session_state:
    st.session_state.force_select_index = None

def load_chats_from_firestore(uid):
    chats_ref = db.collection("users").document(uid).collection("chats")
    docs = chats_ref.order_by("createdAt").stream()

    chats = []
    for doc in docs:
        data = doc.to_dict()
        chats.append({
            "id": doc.id,
            "title": data.get("title", "無題")
        })
    return chats

def save_message(uid, chat_id, role, content):
    messages_ref = (
        db.collection("users")
        .document(uid)
        .collection("chats")
        .document(chat_id)
        .collection("messages")
    )

    messages_ref.add({
        "role": role,
        "content": content,
        "createdAt": firestore.SERVER_TIMESTAMP
    })

def load_messages(uid, chat_id):
    messages_ref = (
        db.collection("users")
        .document(uid)
        .collection("chats")
        .document(chat_id)
        .collection("messages")
        .order_by("createdAt")
    )

    docs = messages_ref.stream()

    messages = []
    for doc in docs:
        data = doc.to_dict()
        messages.append({
            "role": data["role"],
            "content": data["content"],
        })

    return messages


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

                    st.session_state.chats = load_chats_from_firestore(uid)
                    
                    st.success("登録成功")
                    st.session_state.page = "chat"
                    st.rerun()
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
    if st.session_state.user and st.session_state.current_chat_id:
        messages = load_messages(
            st.session_state.user["uid"],
            st.session_state.current_chat_id
        )

        for msg in messages:
            st.chat_message(msg["role"]).write(msg["content"])
    else :
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
                
    prompt = st.chat_input("議題を入力してください…")

    if (prompt):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

    if (prompt and st.session_state.user and st.session_state.current_chat_id):
        save_message(
            uid=st.session_state.user["uid"],
            chat_id=st.session_state.current_chat_id,
            role="user",
            content=prompt
        )

def on_change(key):
    selected_title = st.session_state[key]

    chat_id_map = {c["title"]: c["id"] for c in st.session_state.chats}
    selected_chat_id = chat_id_map[selected_title]

    st.session_state.current_chat_id = selected_chat_id

    st.session_state.page = "chat"

    uid = st.session_state.user["uid"]
    st.session_state.messages = load_messages(uid, chat_id)
    

with st.sidebar:
    # ① 一番上：新規チャット
    if st.button("新規チャット", use_container_width=True):

        if st.session_state.user:
            uid = st.session_state.user["uid"]

            chat_ref = (
                db.collection("users")
                .document(uid)
                .collection("chats")
                .document()
            )

            chat_ref.set({
                "title": "新しいチャット",
                "createdAt": firestore.SERVER_TIMESTAMP
            })

            new_id = chat_ref.id

        else:
            # 未ログイン時（Firestoreに保存しない）
            new_id = f"chat{len(st.session_state.chats) + 1}"

        st.session_state.chats.append({
            "id": new_id,
            "title": "新しいチャット"
        })

        st.session_state.current_chat_id = new_id
        st.session_state.page = "chat"
        st.rerun()

    # ② 真ん中：チャット一覧
    if st.session_state.user is None:
        # 未ログイン時
        st.markdown(
            """
            <div style="
                padding: 11.5rem 1rem;
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
            key='chat_history',
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
