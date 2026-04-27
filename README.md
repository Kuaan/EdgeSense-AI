# EdgeSense-AI
## MCU-Scale Edge Computing & Device Orchestration Platform
EdgeSense-AI is a **lightweight Edge Computing platform** that demonstrates how **real Edge AI infrastructure can be built using microcontrollers** instead of heavy cloud-dependent systems.
The project showcases **Edge Computing running on ESP32-class MCUs**, coordinated by a self-built gateway designed for flexible Industrial IoT deployments.
Unlike traditional IoT platforms relying on large frameworks or proprietary modules, EdgeSense-AI focuses on:

- Minimal hardware footprint
- Full system ownership
- Deployable edge intelligence
- Infrastructure-style device management

---

## Core Idea

> Can microcontrollers act as real edge computers instead of simple sensor nodes?

EdgeSense-AI answers **yes**.

ESP32 devices operate as an **Edge Compute Layer**, executing AI inference, routing data, and managing downstream networks.

---

## System Architecture

```txt
                    ┌────────────────────┐
                    │   Management UI    │
                    └─────────┬──────────┘
                              │ REST API
                    ┌─────────▼──────────┐
                    │  Gateway (Pi 4B)   │
                    │--------------------│
                    │ FastAPI Backend    │
                    │ MQTT Broker        │
                    │ Device Registry    │
                    │ OTA Manager        │
                    └─────────┬──────────┘
                              │ MQTT / WiFi
        ┌─────────────────────┴─────────────────────┐
        │                                           │
 ┌───────────────┐                          ┌───────────────┐
 │ ESP32-S3      │                          │ ESP32 Node    │
 │ Edge AI       │                          │ Edge Router   │
 │ Vision Compute│                          │ LoRa Gateway  │
 └───────────────┘                          └───────┬───────┘
                                                    │ LoRa
                                            ┌───────▼───────┐
                                            │ STM32 Sensor  │
                                            │ Deep Edge     │
                                            └───────────────┘
```

## Architecture Layers
### Lightweight Edge Gateway — Raspberry Pi 4B
A self-built gateway stack, replacing heavy IoT platforms.

- Features:
Async FastAPI control plane
MQTT event backbone
Dynamic device registry
OTA firmware lifecycle
Telemetry storage

- Designed to be:
portable
hackable
infrastructure-like

without Kubernetes, cloud lock-in, or proprietary SDKs.

### Edge Compute Layer — ESP32 Family

- ESP32 devices act as edge computers, not passive endpoints.

ESP32-S3 — Edge AI Vision Node
On-device CNN inference (FOMO / MobileNetV2)
Real-time object detection
Dual-core task separation
Optimized DMA camera pipeline

- Demonstrates TinyML on resource-constrained MCU hardware.

ESP32 Node — Edge Network Router
MQTT client node
WiFi ↔ LoRa bridge
Protocol translation layer
Downstream device aggregation

Extends gateway reach beyond WiFi environments.

### Deep Edge Layer — STM32F103
Ultra-low-level sensing layer.

FreeRTOS scheduler
Long-range LoRa telemetry
Resilient low-bandwidth operation

Represents field-deployed sensor endpoints.

---
### MCU-Level Edge AI
Real-time AI inference running on ESP32-S3 without cloud dependency.

### Self-Built Gateway Infrastructure
Custom gateway replacing heavy IoT stacks with a lightweight asynchronous backend.

### OTA Device Lifecycle Management
Remote firmware deployment
Job tracking
Status monitoring
Version control

### Hybrid Network Topology
- Single system managing:
WiFi devices
LoRa sensor networks
Multi-hop edge communication

### Out-of-Band Monitoring
Health visibility across all layers:

- Gateway:
CPU / RAM / Temperature

- Nodes:
RSSI / SNR / Heartbeat

### 🛠️ Engineering Challenges Solved 🛠️
- ESP32 Camera + WiFi DMA Conflict
- Stabilized concurrent camera streaming and WiFi networking through memory tuning and task isolation.
- Long-Range Packet Corruption
- Implemented defensive JSON parsing for unreliable LoRa transmissions.
- Autonomous Device Onboarding
- Dynamic device registry enabling plug-and-deploy nodes.

### Development Roadmap
Phase	Description
[v] P0-P2	Gateway Core & MQTT Pipeline
[v] P3	OTA Manager
[v] P4	MCU Edge AI Deployment
[v] P5-P6	LoRa Multi-Hop Integration
[ ] P7	Security Hardening
[ ] P8	Event Bus & Edge Automation


---
## >>> Quick Start <<<
Setup Gateway
git clone https://github.com/Kuaan/EdgeSense-AI.git
cd EdgeSense-AI/gateway
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
Deploy Firmware

Flash binaries from:
/firmware


### Project Vision

EdgeSense-AI explores a new direction:
Edge Computing should not require powerful hardware.
This project demonstrates that distributed edge infrastructure can emerge from microcontrollers.

👤 Author
Angus Ku
Embedded Systems • Edge AI • Distributed IoT Infrastructure

