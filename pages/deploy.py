#import streamlit as st
#import paramiko
#from utils.device_utils import deploy_to_device

#def show_deploy():
#    st.header("Deploy to Edge Device")
#    device_ip = st.text_input("Device IP")
#    model_path = st.text_input("Model Path")
#    if st.button("Deploy"):
#        deploy_to_device(device_ip, model_path)
#        st.success("Model deployed successfully")
