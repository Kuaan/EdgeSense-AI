#include <WiFi.h>
#include <PubSubClient.h> // 請在 Library Manager 安裝
#include <LoRa.h>

// WiFi & MQTT 設定
const char* ssid = "Ang";
const char* password = "a22560540";
//const char* mqtt_server = "broker.hivemq.com"; // 測試用公共伺服器
const char* mqtt_server = "172.20.10.4"; // 這裡請填入你 Raspberry Pi 的實際 IP

WiFiClient espClient;
PubSubClient client(espClient);
// 在 loop() 的最後一個大括號之後貼上這些：

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // 循環直到重新連接成功
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // 建立一個隨機的 Client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    // 嘗試連接
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // 連接成功後可以重新訂閱主題 (如果需要的話)
      // client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // 等 5 秒再重試
      delay(5000);
    }
  }
}

void setup() {
    Serial.begin(115200);
    // 1. 初始化 WiFi & LoRa (略，同之前)
    setup_wifi();
    LoRa.setPins(5, 14, 2);
    LoRa.begin(433E6);
    if (!LoRa.begin(433E6)) {
      Serial.println("LoRa Error! Check your wiring.");
      while (1); // 停在這裡，方便你檢查硬體
    }
    Serial.println("LoRa OK!");
    
    client.setServer(mqtt_server, 1883);
}

// ESP32.ino 局部修正
void loop() {
    if (!client.connected()) reconnect();
    client.loop();

    int packetSize = LoRa.parsePacket();
    if (packetSize) {
        String msg = "";
        while (LoRa.available()) { msg += (char)LoRa.read(); }
        
        // 清理一下從 LoRa 拿到的字串 (去掉可能存在的 \r\n)
        msg.trim();

        char attributes[128];
        // 1. 格式對齊 Gateway：必須有 "data" 欄位
        // 2. 注意：rssi 和 snr 是整數和浮點數
        snprintf(attributes, sizeof(attributes), 
                 "{\"data\":\"%s\",\"rssi\":%d,\"snr\":%.1f}", 
                 msg.c_str(), LoRa.packetRssi(), LoRa.packetSnr());
        
        // 3. 重要：Topic 改為 "devices/..." (複數)
        // 這樣 Gateway 的 on_event (v13.5) 才能正確拆解 parts[1]
        client.publish("devices/STM32_01/event", attributes);
        
        Serial.println("Forwarded to Gateway: " + String(attributes));
    }
}