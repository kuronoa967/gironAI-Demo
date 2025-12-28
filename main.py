import streamlit as st

st.title("ボタン固定の例")
st.write("長いコンテンツ..." * 100) # スクロール用

# 画面最下部の領域にボタンを配置
with st._bottom:
    if st.button("送信"):
        st.write("ボタンが押されました")
