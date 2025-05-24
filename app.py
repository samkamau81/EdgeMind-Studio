import streamlit as st

st.set_page_config(page_title="Embedded AI Agent IDE", layout="wide")
st.sidebar.title("Navigation")
pages = ["Editor", "Train & Optimize", "Deploy", "Monitor & Maintain"]
page = st.sidebar.radio("Go to", pages)

if page == "Editor":
    from pages.editor import show_editor
    show_editor()
elif page == "Train & Optimize":
    from pages.train import show_train
    show_train()
elif page == "Deploy":
    from pages.deploy import show_deploy
    show_deploy()
elif page == "Monitor & Maintain":
    from pages.monitor import show_monitor
    show_monitor()
