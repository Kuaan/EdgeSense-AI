#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASS";
const char* mqtt_server = "YOUR_MQTT_BROKER_IP";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void publish_telemetry() {
  String topic = "edgesense-ai/telemetry/node01";
  String payload = "{\"temp\":25.3}";
  client.publish(topic.c_str(), payload.c_str());
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("esp32-node-01")) {
    } else {
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();
  publish_telemetry();
  delay(5000);
}
