import streamlit as st
import pandas as pd
from utils.maintenance import get_logs, update_model

def show_monitor():
    st.header("Monitor & Maintain")
    device_id = st.text_input("Device ID")
    logs = get_logs(device_id)
    st.dataframe(pd.DataFrame(logs))
    if st.button("Update Model"):
        model_path = st.text_input("New Model Path")
        update_model(device_id, model_path)
        st.success("Model updated on device")
