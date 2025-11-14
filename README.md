🛰️ EdgeSense-AI
Intelligent Secure Edge Device Management System
(Edge AI · BMC-style Management · FreeRTOS · Multi-Protocol Communication · Cybersecurity · OTA)

📌 Overview

EdgeSense-AI is a secure and intelligent edge device management platform built with Raspberry Pi, STM32, ESP32, and ESP32-S3.
It integrates:

Multi-protocol communication (BLE / WiFi / LoRa / UART)

FreeRTOS real-time task management (STM32)

Secure OTA firmware update

Cybersecurity (Diffie–Hellman, AES-GCM, device identity)

Edge AI inference using ESP32-S3 camera

Redfish-style device management API (Raspberry Pi)

Web-based UI for monitoring and control (Python Flask)

Industrial-grade layered architecture (Device → Protocol → Security → Management)

This project demonstrates complete embedded system engineering capabilities—from hardware, protocols, and security to device management, edge AI, and gateway design.

📦 System Architecture
 +-------------------------------------------------------------------+
 |                   Web Dashboard (Flask / Bootstrap)               |
 |   - Device List / Sensors / Logs                                  |
 |   - OTA Upload & Control                                           |
 |   - Key Exchange / Authentication                                 |
 |   - Live Telemetry (WebSocket)                                    |
 +-----------------------------+-------------------------------------+
                               |
                          HTTPS / REST
                               |
                     +---------+----------+
                     | Raspberry Pi 4B    |  <-- Edge Gateway
                     | - Redfish-style API|
                     | - Device Registry  |
                     | - Secure Key Mgmt  |
                     | - MQTT / LoRa Hub  |
                     +---------+----------+
                               |
      +-------------+-----------+------------+------------------+
      |             |           |            |                  |
     BLE        WiFi MQTT     LoRa        UART RS485         UWB
      |             |           |            |                  |
+-----+----+   +----+------+ +--+----+  +----+-----+      +----+------+
|ESP32-BLE|   |ESP32 Node | |LoRa Node| |STM32 RTOS|      |ESP32 UWB  |
+---------+   +-----------+ +---------+ +----------+      +-----------+
                      |
               +---------------+
               | ESP32-S3 CAM  |
               |  Edge AI      |
               +---------------+

🔧 Hardware Used

Raspberry Pi 4B x1 — Gateway + REST API + Web Dashboard

STM32F103RCT6 x1 — FreeRTOS Industrial Node

ESP32 (multiple units) — BLE / WiFi / LoRa nodes

ESP32-S3 + Camera (x2) — Edge AI Vision Node

Various Arduino sensor modules (I2C / SPI / UART)

🚀 Features
🧩 1. Multi-Protocol Communication

BLE (pairing, notifications)

WiFi MQTT (TLS encrypted telemetry)

LoRa long-range telemetry

UART (Modbus-style protocol)

Unified TLV packet format for all nodes

⚙ 2. FreeRTOS (STM32)

Sensor task, communication task, watchdog task

Queue, mutex, event groups

I2C / SPI / UART HAL drivers

State machine design for industrial use

Hardware watchdog enabled

🔐 3. Cybersecurity

ECC / Curve25519 Diffie–Hellman key exchange

AES-128-GCM encryption for all packets

Device identity authentication

Challenge–response mechanism

Signed OTA firmware (SHA-256 + signature)

Secure boot & rollback protection

📡 4. OTA Update System

Gateway sends firmware to target device

Nodes verify firmware signature

OTA progress reporting through MQTT/WebSocket

Automatic fallback on failure

🧠 5. Edge AI (ESP32-S3)

TensorFlow Lite Micro inference

Quantized MobileNet model (<1 MB)

Real-time image classification

Human / pet / anomaly detection

Event trigger → Gateway alerts

🧰 6. Device Management (BMC / Redfish Style)

REST API inspired by Redfish schema:

/redfish/v1/Devices

/redfish/v1/Telemetry

/redfish/v1/Actions/OTA.Update

/redfish/v1/Security/KeyExchange

Features:

Token-based authentication

Device registry

JSON telemetry format

Action-based control API

🌐 7. Web Management Console

Device status overview

Real-time telemetry display (Plotly charts)

OTA firmware upload and control

Key exchange & security validation

Live AI camera preview (ESP32-S3 stream)

Built with:

Flask

Flask-SocketIO

Bootstrap

Plotly

📁 Project Structure
EdgeSense-AI/
│
├── gateway/                   # Raspberry Pi Gateway
│   ├── api/
│   │   ├── redfish.py         # REST API
│   │   ├── security.py        # Key mgmt, DH, tokens
│   │   ├── ota.py             # OTA orchestrator
│   │   └── registry.py        # Device database
│   ├── web/
│   │   ├── templates/
│   │   ├── static/
│   │   └── dashboard.py
│   ├── mqtt/
│   ├── lora/
│   └── run_gateway.py
│
├── stm32_rtOS/
│   ├── Core/
│   ├── Drivers/
│   ├── FreeRTOS/
│   └── app/
│       ├── sensor_task.c
│       ├── comm_task.c
│       └── security.c
│
├── esp32_nodes/
│   ├── wifi_node/
│   ├── ble_node/
│   ├── lora_node/
│   └── uart_bridge/
│
├── esp32s3_ai/
│   ├── camera_stream/
│   ├── tflite_micro/
│   └── ai_inference/
│
├── common/
│   ├── protocol_tlv.h
│   ├── crypto/
│   └── utils/
│
├── docs/
│   ├── architecture.md
│   ├── protocol.md
│   ├── ota_flow.md
│   └── security_design.md
│
└── README.md

🛠 Setup Guide
1. Raspberry Pi (Gateway)
Install dependencies
sudo apt update
sudo apt install python3 python3-pip mosquitto
pip3 install flask flask-socketio pycryptodome paho-mqtt

Start the gateway
python3 gateway/run_gateway.py

2. ESP32 Nodes

Use PlatformIO or Arduino IDE:

Upload:
- wifi_node
- ble_node
- lora_node
- uart_bridge

3. STM32 (FreeRTOS)

Generate code using STM32CubeMX →
Build with Keil / IAR / PlatformIO →
Flash to device.

4. Web Dashboard
cd gateway/web
python3 dashboard.py


Open in browser:
➡ http://<gateway-ip>:8080

🔌 REST API (Redfish-style)
List devices
GET /redfish/v1/Devices

Get telemetry
GET /redfish/v1/Telemetry/<id>

Trigger OTA
POST /redfish/v1/Actions/OTA.Update
{
  "device": "esp32-node-01",
  "firmware": "firmware_v2.bin",
  "signature": "sig.txt"
}

Key exchange
POST /redfish/v1/Security/KeyExchange

🔒 Security Architecture
[Gateway] --DH--> [Node]
       <--- DH ---
(AES Session Key Established)

Encrypted Payloads:
[Gateway] --AES-GCM--> Commands / Telemetry
[Node]    --AES-GCM--> Telemetry / Logs

OTA Process:
firmware.bin + signature.sha256
Node verifies → applies update → reports progress

🧪 Development Notes

All nodes follow a unified TLV packet format

All sensor data reported in JSON

AI models quantized to remain <1 MB

LoRa node reports every 30 seconds

STM32 uses watchdog + fail-safe design

📜 License

MIT License

🙌 Author

EdgeSense-AI — by Angus Ku (2025)
PRs and Issues are welcome!
