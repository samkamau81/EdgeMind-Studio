import streamlit as st
import pandas as pd
import json
import requests
import time
from datetime import datetime
import importlib
from flask import Flask, request, jsonify
import threading

# Optional Gemini import if selected
try:
    import google.generativeai as genai
except ImportError:
    pass

# Create Flask server for ESP communication
flask_app = Flask(__name__)
agent_actions = {"motor": "OFF", "led": "OFF"}

@flask_app.route('/streamlit_esp', methods=['GET'])
def get_agent_actions():
    return jsonify(agent_actions)

def run_flask_server():
    flask_app.run(host='0.0.0.0', port=8503)

# Start Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask_server)
flask_thread.daemon = True
flask_thread.start()

# Streamlit app configuration
st.set_page_config(page_title="EmbedMind Studio", layout="wide")

# Title and Description
st.title("EmbedMind Studio - Hardware Agent Builder IDE")
st.markdown("A smart IDE for building AI agents on embedded devices with support for LLMs and sensor simulation.")

# Sidebar: Project Configuration
with st.sidebar:
    st.image("https://github.com/samkamau81/EmbedMind-Studio/blob/main/embedmind_logo.jpg")
st.sidebar.header("🔧 Project Settings")
project_name = st.sidebar.text_input("Project Name", "Fire Safety Agent")
device_type = st.sidebar.selectbox("WiFi Module", ["ESP8266", "Raspberry Pi"])
server_url = st.sidebar.text_input("Server URL", "http://192.168.100.6:8502/esp_streamlit")

# LLM Configuration
st.sidebar.markdown("### 🧠 Language Model Settings")
llm_provider = st.sidebar.selectbox("LLM Provider", ["None", "Gemini", "OpenAI"])
llm_api_key = st.sidebar.text_input("LLM API Key", type="password")

# Sensor Selection and Simulation
st.sidebar.markdown("### 🌡 Sensor Configuration")
sensor_options = ["Smoke", "Temperature", "Humidity", "CO", "Flame"]
selected_sensors = st.sidebar.multiselect("Sensors", sensor_options, default=["Smoke"])

sensor_values = {}
for sensor in selected_sensors:
    if sensor == "Smoke":
        sensor_values["smoke"] = st.sidebar.slider("Smoke (ppm)", 0, 1000, 30)
    elif sensor == "Temperature":
        sensor_values["temperature"] = st.sidebar.slider("Temperature (°C)", -10, 100, 25)
    elif sensor == "Humidity":
        sensor_values["humidity"] = st.sidebar.slider("Humidity (%)", 0, 100, 45)
    elif sensor == "CO":
        sensor_values["co"] = st.sidebar.slider("CO (ppm)", 0, 500, 20)
    elif sensor == "Flame":
        sensor_values["flame"] = st.sidebar.selectbox("Flame Detected?", ["Yes", "No"])

st.subheader("📡 Incoming Data from ESP8266")

if st.button("🔄 Refresh Incoming Data"):
    try:
        esp_data_url = server_url.replace("/esp_streamlit", "/esp_data")
        response = requests.get(esp_data_url, timeout=5)
        if response.status_code == 200:
            incoming_data = response.json()
            st.write(f"Showing {len(incoming_data)} latest packets:")
            st.json(incoming_data)
        else:
            st.warning(f"Server responded with status {response.status_code}")
    except requests.exceptions.Timeout:
        st.error("Connection timeout - check if ESP is powered on and connected")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed: {str(e)}")

# Agent Function Editor
st.subheader("🧠 Write Your Agent")
default_code = '''def tool_function(sensor_data, llm=None):
    if not llm:
        return {"motor": "OFF", "led": "OFF"}
    
    prompt = f"""
    Given a smoke reading of {sensor_data['smoke']} ppm:
    Should we activate the motor (ventilation) and warning LED?
    Return exactly in this format: MOTOR:ON/OFF, LED:ON/OFF
    """
    
    response = llm.generate_content(prompt)
    output = response.text.strip()
    
    return {
        "motor": "ON" if "MOTOR:ON" in output else "OFF",
        "led": "ON" if "LED:ON" in output else "OFF"
    }
'''
agent_code = st.text_area("Define your agent tool_function", default_code, height=250)

# Compile and evaluate agent
compiled_function = None
llm_model = None

if llm_provider == "Gemini" and llm_api_key:
    try:
        genai.configure(api_key=llm_api_key)
        llm_model = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        st.sidebar.error(f"Gemini setup error: {e}")

elif llm_provider == "OpenAI" and llm_api_key:
    try:
        import openai
        openai.api_key = llm_api_key
        llm_model = openai
    except Exception as e:
        st.sidebar.error(f"OpenAI setup error: {e}")

try:
    exec(agent_code, globals())
    compiled_function = globals().get("tool_function")
except Exception as e:
    st.error(f"Function compile error: {e}")

# Agent Simulation
st.subheader("🚦 Simulate and Run Agent")
send_to_device = st.checkbox("Send actions to hardware", value=True)

if st.button("▶️ Run Simulation"):
    if compiled_function:
        try:
            result = compiled_function(sensor_values, llm=llm_model)
            st.success("✅ Agent Output")
            st.json(result)
            
            # Update agent actions that ESP will fetch
            agent_actions.update(result)

            if send_to_device:
                payload = {
                    "project": project_name,
                    "device": device_type,
                    "sensor_data": sensor_values,
                    "agent_actions": result,
                    "timestamp": datetime.now().isoformat()
                }

                try:
                    response = requests.post(server_url, json=payload)
                    if response.status_code == 200:
                        st.success("📤 Sent to hardware")
                        st.json(response.json())
                    else:
                        st.error(f"Failed to send, status {response.status_code}")
                except Exception as e:
                    st.error(f"Communication error: {e}")
        except Exception as err:
            st.error(f"Agent simulation error: {err}")
    else:
        st.warning("No valid function defined.")

# Save Project
st.subheader("💾 Save Project Configuration")
if st.button("💡 Save Project"):
    project_data = {
        "project_name": project_name,
        "device_type": device_type,
        "server_url": server_url,
        "sensors": selected_sensors,
        "code": agent_code,
        "llm_provider": llm_provider,
        "sample_input": sensor_values
    }
    st.download_button("📥 Download Project JSON", json.dumps(project_data, indent=4),
                       file_name=f"{project_name.replace(' ', '_')}.json", mime="application/json")

st.markdown("---")
st.caption("📡 EmbedMind Studio 2025 – Build. Simulate. Deploy.")
