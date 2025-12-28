import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")

if "chats" not in st.session_state:
    st.session_state.chats = [
        {"id": "chat1", "title": "働き方について"},
        {"id": "chat2", "title": "将来の不安"},
        {"id": "chat3", "title": "AIとの対話"},
    ]

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

with st.sidebar:
    # ① 一番上：新規チャット
    if st.button("＋ 新規チャット", use_container_width=True):
        new_id = f"chat{len(st.session_state.chats) + 1}"
        st.session_state.chats.append(
            {"id": new_id, "title": "新しいチャット"}
        )
        st.session_state.current_chat_id = new_id

    # ② 真ん中：チャット一覧
    chat_titles = [c["title"] for c in st.session_state.chats]
    chat_id_map = {c["title"]: c["id"] for c in st.session_state.chats}

    selected_chat = option_menu(
        menu_title="None",
        options=chat_titles,
        icons=["chat"] * len(chat_titles),
    )

    if selected_chat:
        st.session_state.current_chat_id = chat_id_map[selected_chat]

    # ③ 一番下：アカウントボタン（今は仮）
    if st.button("アカウント", use_container_width=True):
        st.session_state.page = "account"

st.header("メインチャット画面")

if st.session_state.current_chat_id is None:
    st.info("左のサイドバーからチャットを選択してください")
else:
    st.write("選択中のチャットID:")
    st.code(st.session_state.current_chat_id)
