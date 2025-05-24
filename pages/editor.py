import streamlit as st
from streamlit_ace import st_ace
import os
from utils.model_utils import save_project

def show_editor():
    st.header("Code Editor")
    project_name = st.text_input("Project Name")
    code = st_ace(language="python", theme="monokai", key="editor")
    if st.button("Save"):
        save_project(project_name, code)
        st.success(f"Saved {project_name}")
