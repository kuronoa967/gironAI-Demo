import streamlit as st

# サイドバーに通常のコンテンツを配置
st.sidebar.title("メニュー")
st.sidebar.write("ここに通常のリンクや設定を配置します。" * 50)

# 下部に固定したいボタン用のコンテナ
with st.sidebar.container(key="sidebar_bottom"):
    if st.button("ログアウト", use_container_width=True):
        st.write("ログアウトしました")

# CSSでコンテナをサイドバー最下部に固定
st.html("""
    <style>
        /* keyで指定したコンテナを最下部に配置 */
        .st-key-sidebar_bottom {
            position: absolute;
            bottom: 20px;
            width: 90%;
        }
    </style>
""")
