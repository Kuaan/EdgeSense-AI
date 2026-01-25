#v8.0
import paho.mqtt.client as mqtt
from app.mqtt import handlers

BROKER = "localhost"
PORT = 1883

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")

    # 訂閱 Heartbeat
    client.subscribe("devices/+/heartbeat")
    client.message_callback_add("devices/+/heartbeat", handlers.on_heartbeat)

    # 訂閱 OTA Status
    client.subscribe("devices/+/ota_status")
    client.message_callback_add("devices/+/ota_status", handlers.on_ota_status)

    print("[MQTT] Subscribed to heartbeat and ota_status")

def start():
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()


'''v5.4
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

mqtt_client = mqtt.Client()


def start():
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()
'''

'''v5.2
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
        
    def publish(self, topic: str, payload: dict):
        try:
                self.client.publish(topic, json.dumps(payload))
                return True
        except Exception as e:
                print(f"[MQTT] publish error: {e}")
                return False

    def on_message(self, client, userdata, msg):
        topic = msg.topic

        if topic.endswith("/heartbeat"):
            on_heartbeat(topic, msg.payload)

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        self.client.loop_start()

mqtt_client = MqttClient()
'''
