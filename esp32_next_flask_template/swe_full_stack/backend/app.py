from flask import Flask, request
import paho.mqtt.client as mqtt
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Crucial for your React app

mqtt_client = mqtt.Client()
mqtt_client.connect("broker.hivemq.com", 1883, 60)

@app.route('/toggle', methods=['POST'])
def toggle_led():
    state = request.json.get('state') # "ON" or "OFF"
    mqtt_client.publish("riverwalk/led", state)
    return {"status": "sent", "state": state}

if __name__ == '__main__':
    app.run(port=5000)