// #define WIFI_SSID     "DrayTek_M"
// #define WIFI_PASSWORD "1qasde32"
// #define MQTT_HOST     "192.168.1.20"  
#include <WiFi.h>
#include <PubSubClient.h>
#include <HTTPClient.h>
#include <Update.h>

#define BLED 2

#define WIFI_SSID     "Ang"
#define WIFI_PASSWORD "22560540"
#define MQTT_HOST     "172.20.10.4"
#define MQTT_PORT     1883

#define HEARTBEAT_INTERVAL_MS 5000

String fw_version= "v7.1.3"; 


WiFiClient espClient;
PubSubClient mqtt(espClient);

String deviceUID;
unsigned long lastHeartbeat = 0;

String currentJobId = "";

unsigned long nowMs=0;
unsigned long lastMs=0;


void bledBlinkingMs(int ms){
  nowMs=millis();
  if(nowMs-lastMs > ms){
    digitalWrite(BLED, !digitalRead(BLED));
    lastMs=nowMs;
  }
}


String getDeviceUID() {
  uint64_t mac = ESP.getEfuseMac();
  char uid[13];

  sprintf(uid,"%04X%08X",(uint16_t)(mac >> 32),(uint32_t)mac);

  return String(uid);
}

String topicHeartbeat() {
  return "devices/" + deviceUID + "/heartbeat";
}

String topicStatus() {
  return "devices/" + deviceUID + "/status";
}

String topicOTA() {
  return "devices/" + deviceUID + "/ota";
}

String topicOTAResult() {
  return "devices/" + deviceUID + "/ota_status";
}

/* ========= MQTT REPORT ========= */
void publishStatus(const String& status) {
  String payload =
  "{\"status\":\"" + status +
  "\",\"fw_version\":\"" +
  fw_version +
  "\"}";
  mqtt.publish(topicStatus().c_str(), payload.c_str(), true);
}

void publishOTAResult(const String& status) {
  String payload =
  "{"
  "\"job_id\":\"" + currentJobId + "\","
  "\"status\":\"" + status + "\","
  "\"fw_version\":\"" + fw_version + "\""
  "}";

  mqtt.publish(topicOTAResult().c_str(),payload.c_str(),false);
}



/* ========= OTA CORE ========= */
void doOTA(String url,String version,String md5) {

  HTTPClient http;
  WiFiClient client;

  publishOTAResult("downloading");
  http.begin(client, url);

  int code = http.GET();

  if (code != HTTP_CODE_OK) {
    publishOTAResult("failed");
    http.end();
    return;
  }

  int size = http.getSize();

  if (!Update.begin(size)) {
    publishOTAResult("failed");
    http.end();
    return;
  }

  //
  // ⭐ 官方 MD5
  //
  if(md5.length()>0){
    Update.setMD5(md5.c_str());
  }

  publishOTAResult("flashing");

  size_t written =Update.writeStream(*http.getStreamPtr());

  if (written != size) {
    Update.abort();
    publishOTAResult("failed");
    http.end();
    return;
  }

  if (!Update.end(true)) {
    publishOTAResult("failed");
    http.end();
    return;
  }

  publishOTAResult("success");
  http.end();
  delay(1000);
  ESP.restart();
}

/* ========= MQTT CALLBACK ========= */
String jsonValue(String msg,String key){
  int p=msg.indexOf("\""+key+"\"");
  if(p<0) return "";
  int p2=msg.indexOf("\"",p+key.length()+3);
  int p3=msg.indexOf("\"",p2+1);
  return msg.substring(p2+1,p3);
}

void onMqttMessage(char* topic,byte* payload,unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  //
  // ⭐ 保留你的 print
  //
  Serial.println("[MQTT] OTA JOB: " + msg);
  String url = jsonValue(msg,"url");
  String version = jsonValue(msg,"version");
  String job_id = jsonValue(msg,"job_id");
  String md5 = jsonValue(msg,"md5");
  currentJobId = job_id;

  if(url==""){
    Serial.println("Invalid OTA");
    return;
  }

  doOTA(url,version,md5);
}

/* ========= HEARTBEAT ========= */
void sendHeartbeat() {
  String payload =
  "{\"fw_version\":\"" +
  fw_version +
  "\"}";

  mqtt.publish(topicHeartbeat().c_str(),payload.c_str(),false);
  //
  // ⭐ 保留你的 print
  //
  Serial.println(topicHeartbeat() +" ," +payload);
}

/* ========= SETUP ========= */
void setup() {
  Serial.begin(115200);
  pinMode(BLED, OUTPUT);
  digitalWrite(BLED, LOW );
  //
  // ⭐ 保留你的 print
  //
  Serial.println("Version: "+fw_version);
  deviceUID = getDeviceUID();
  //
  // ⭐ 保留你的 print
  //
  Serial.println("Device UID: " + deviceUID);

  WiFi.begin(WIFI_SSID,WIFI_PASSWORD);

  while (WiFi.status()!= WL_CONNECTED) {
    delay(500);
  }

  mqtt.setServer(MQTT_HOST,MQTT_PORT);

  mqtt.setCallback(onMqttMessage);

  while (!mqtt.connected()) {
    mqtt.connect(deviceUID.c_str());
    delay(500);
  }
  mqtt.subscribe(
    topicOTA().c_str());

  publishStatus("online");
}


/* ========= LOOP ========= */
void loop() {
  mqtt.loop();
  bledBlinkingMs(500);

  unsigned long now = millis();

  if (now - lastHeartbeat > HEARTBEAT_INTERVAL_MS) {
    lastHeartbeat = now;
    sendHeartbeat();
  }
}
