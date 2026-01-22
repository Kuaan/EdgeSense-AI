import json
from app.main import mqtt
from app.mqtt import topics


def publish_status(device_id: str, status: str):
    topic = topics.status_topic(device_id)
    mqtt.client.publish(topic, json.dumps({"status": status}), retain=True)


def publish_ota(device_id: str, payload: dict):
    topic = topics.ota_topic(device_id)
    mqtt.client.publish(topic, json.dumps(payload))

