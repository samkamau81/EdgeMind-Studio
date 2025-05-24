import streamlit as st
import tensorflow as tf
from utils.model_utils import optimize_model

def show_train():
    st.header("Train & Optimize Model")
    model_type = st.selectbox("Model Type", ["TensorFlow", "PyTorch"])
    dataset = st.file_uploader("Upload Dataset", type=["csv", "npy"])
    if st.button("Train"):
        # Placeholder for training logic
        st.info("Training model...")
    if st.button("Optimize for Edge"):
        model_path = st.text_input("Model Path")
        optimized_path = optimize_model(model_path)
        st.success(f"Optimized model saved at {optimized_path}")
