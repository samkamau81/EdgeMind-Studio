from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

data_log = []  # Store incoming data temporarily

@app.route('/esp_streamlit', methods=['POST'])
def receive_data():
    try:
        payload = request.json
        payload["received_at"] = datetime.now().isoformat()
        data_log.append(payload)

        # Extract motor/LED command if available
        actions = payload.get("agent_actions", {})
        return jsonify(actions)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/esp_data', methods=['GET'])
def get_data():
    return jsonify(data_log[-10:])  # Send last 10 entries for Streamlit to display

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8502)
