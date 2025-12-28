import streamlit as st

with st.sidebar:
    st.title("サイドバー")
    st.write("上部のコンテンツ")
    
    # 残りのスペースをすべて埋めるスペーサー
    st.space(size="stretch")
    
    # スペーサーの後にボタンを置くと、結果的に一番下へ押し出される
    if st.button("設定"):
        st.write("設定画面へ")
