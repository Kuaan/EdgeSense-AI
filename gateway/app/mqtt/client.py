import paho.mqtt.client as mqtt
from app.mqtt.handlers import on_heartbeat

MQTT_BROKER = "localhost"
MQTT_PORT = 1883


class MqttClient:
    def __init__(self):
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with result code {rc}")

        # wildcard subscribe（正確位置）
        client.subscribe("devices/+/heartbeat")

        # 預留
        # client.subscribe("devices/+/status")
        # client.subscribe("devices/+/telemetry")

    def on_message(self, client, userdata, msg):
        topic = msg.topic

        if topic.endswith("/heartbeat"):
            on_heartbeat(topic, msg.payload)

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        self.client.loop_start()

mqtt_client = MqttClient()
