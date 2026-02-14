#v8.5 app/mqtt/client.py
import os
import paho.mqtt.client as mqtt
from app.mqtt import handlers

BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))

mqtt_client = mqtt.Client()
# -------------------------
# CONNECT
# -------------------------
def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    client.subscribe("devices/+/heartbeat")
    client.message_callback_add(
        "devices/+/heartbeat",
        handlers.on_heartbeat
    )
    client.subscribe("devices/+/ota_status")
    client.message_callback_add(
        "devices/+/ota_status",
        handlers.on_ota_status
    )
    print("[MQTT] Subscribed to heartbeat and ota_status")
# -------------------------
# START
# -------------------------
def start():
    mqtt_client.on_connect = on_connect
    try:
        mqtt_client.connect(BROKER, PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"[MQTT] Connection failed: {e}")
# -------------------------
# PUBLISH  (⭐ FIXED)
# -------------------------
def publish(topic, msg):
    mqtt_client.publish(topic, msg)

