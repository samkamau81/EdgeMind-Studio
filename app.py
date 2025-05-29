import streamlit as st
import requests
import json
import google.generativeai as genai
from datetime import datetime
from fastapi import FastAPI, Request
import uvicorn
import threading
import time

# Configure Gemini API
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# FastAPI app to handle POST from ESP8266
fastapi_app = FastAPI()
received_data = {}
data_history = []

def decide_action(sensor_data):
    prompt = f"""
    Smoke sensor reading: {sensor_data['smoke']} ppm
    (Note: Normal air is 0-20 ppm, dangerous levels are above 60 ppm)
    
    Should we activate the motor (for ventilation) and warning LED?
    Return response in this exact format: "MOTOR:ON/OFF, LED:ON/OFF"
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.strip()

@fastapi_app.post("/esp")
async def esp_post(request: Request):
    global received_data, data_history
    body = await request.json()
    received_data = body
    body['timestamp'] = datetime.now().isoformat()
    data_history.append(body.copy())
    
    # Keep only the last 50 readings
    if len(data_history) > 50:
        data_history.pop(0)
    
    # Get Gemini's decision
    decision = decide_action(body)
    motor = "ON" if "MOTOR:ON" in decision else "OFF"
    led = "ON" if "LED:ON" in decision else "OFF"
    
    return {
        "status": "received",
        "actions": {
            "motor": motor,
            "led": led
        }
    }

def run_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8502, log_level="warning")

threading.Thread(target=run_fastapi, daemon=True).start()

# Streamlit Interface
st.title("🔥 Smoke Detection System")
st.markdown("ESP8266 + Smoke Sensor + Motor/LED Control")

# Sidebar for simulation
st.sidebar.header("Sensor Simulation")
smoke = st.sidebar.slider("Smoke Level (ppm)", 0, 1000, 30)

if st.sidebar.button("Simulate ESP8266 Data Upload"):
    sensor_data = {"smoke": smoke}
    try:
        response = requests.post(
            "http://localhost:8502/esp_streamlit",
            json=sensor_data,
            headers={"Content-Type": "application/json"}
        )
        st.sidebar.success(f"Response: {response.json()}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Main display area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Live Sensor Data")
    data_placeholder = st.empty()
    
    st.subheader("🚦 Current Status")
    status_placeholder = st.empty()

with col2:
    st.subheader("📈 Data History")
    history_placeholder = st.empty()

# Function to update the live data display
def update_display():
    if received_data:
        # Live data card
        smoke_level = received_data.get('smoke', 0)
        danger_level = "⚠️ DANGER" if smoke_level > 60 else "✅ Normal"
        
        data_placeholder.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; background: #f0f2f6; margin-bottom: 20px;">
            <h3 style="margin-top: 0;">Smoke Level</h3>
            <h1 style="color: {'red' if smoke_level > 60 else 'green'}; text-align: center;">{smoke_level} ppm</h1>
            <p style="text-align: center; font-size: 1.2em;">{danger_level}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Status card
        decision = decide_action(received_data)
        motor_status = "🟢 ON" if "MOTOR:ON" in decision else "🔴 OFF"
        led_status = "🟢 ON" if "LED:ON" in decision else "🔴 OFF"
        
        status_placeholder.markdown(f"""
        <div style="border-radius: 10px; padding: 20px; background: #f0f2f6;">
            <h3 style="margin-top: 0;">Actuator Status</h3>
            <p style="font-size: 1.2em;">Motor: {motor_status}</p>
            <p style="font-size: 1.2em;">LED: {led_status}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # History chart
        if data_history:
            history_df = pd.DataFrame(data_history)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            history_placeholder.line_chart(
                history_df.set_index('timestamp')['smoke'],
                use_container_width=True
            )

# Auto-refresh every second
while True:
    update_display()
    time.sleep(1)
    st.rerun()