import streamlit as st

st.set_page_config(layout="wide")

# -----------------------------
# 仮のデータ（後でFirestoreに置き換える）
# -----------------------------
if "chats" not in st.session_state:
    st.session_state.chats = [
        {"id": "chat1", "title": "働き方について"},
        {"id": "chat2", "title": "将来の不安"},
    ]

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

with st.sidebar:
    st.title("AI Chat")

    # 新規チャット
    if st.button("＋ 新規チャット", use_container_width=True):
        new_id = f"chat{len(st.session_state.chats) + 1}"
        st.session_state.chats.append(
            {"id": new_id, "title": "新しいチャット"}
        )
        st.session_state.current_chat_id = new_id

    st.divider()
    st.subheader("チャット一覧")

    for chat in st.session_state.chats:
        if st.button(
            chat["title"],
            key=chat["id"],
            use_container_width=True
        ):
            st.session_state.current_chat_id = chat["id"]

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .sidebar-bottom {
            margin-top: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-bottom">', unsafe_allow_html=True)
    if st.button("アカウント", use_container_width=True):
        st.session_state.page = "account"
    st.markdown('</div>', unsafe_allow_html=True)

st.header("チャット")

if st.session_state.current_chat_id is None:
    st.info("チャットを選択するか、新規チャットを作成してください")
else:
    st.write(f"現在のチャット: {st.session_state.current_chat_id}")

    # 仮の会話履歴
    st.markdown("**ユーザー:** 自分の意見を深めたい")
    st.markdown("**AI:** それについてもう少し詳しく教えてください")

st.markdown(
    """
    <style>
    .chat-input {
        position: fixed;
        bottom: 0;
        left: 25%;
        width: 75%;
        background: white;
        padding: 1rem;
        border-top: 1px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="chat-input">', unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "メッセージを入力",
        label_visibility="collapsed"
    )

with col2:
    if st.button("送信"):
        st.write("送信:", user_input)

st.markdown('</div>', unsafe_allow_html=True)
