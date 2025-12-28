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

chat_titles = [chat["title"] for chat in st.session_state.chats]
chat_id_map = {chat["title"]: chat["id"] for chat in st.session_state.chats}

with st.sidebar:
    st.subheader("チャット")

    selected_chat_title = option_menu(
        menu_title=None,
        options=chat_titles,
        icons=["chat"] * len(chat_titles),
        orientation="vertical",
        styles={
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "0px",
            },
            "nav-link-selected": {
                "background-color": "#2E7BF6",
            },
        },
    )

if selected_chat_title:
    st.session_state.current_chat_id = chat_id_map[selected_chat_title]

st.header("メインチャット画面")

if st.session_state.current_chat_id is None:
    st.info("左のサイドバーからチャットを選択してください")
else:
    st.write("選択中のチャットID:")
    st.code(st.session_state.current_chat_id)

with st.sidebar:
    if st.button("＋ 新規チャット", use_container_width=True):
        new_id = f"chat{len(st.session_state.chats) + 1}"
        new_title = "新しいチャット"

        st.session_state.chats.append(
            {"id": new_id, "title": new_title}
        )
        st.session_state.current_chat_id = new_id

    st.divider()
