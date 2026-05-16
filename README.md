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
## 🏗️ Architecture Layers (Bottom-Up Infrastructure)

EdgeSense-AI maps physical-to-digital telemetry across three distinct operational layers, moving from deep field sensing up to the central orchestration control plane.

### 1. Deep Edge Layer — LoRa Sensor Topology
Designed to extend operational visibility into low-bandwidth, non-IP field environments.

* **STM32F103 Node (The Endpoint):**
    * **Deterministic OS:** Driven by **FreeRTOS** for strict, time-critical sensor sampling.
    * **Resilient Telemetry:** Uses low-overhead LoRa transmission optimized for unstable links.
    * **Fail-Safe Design:** Operates autonomously at the field perimeter, even during backhaul disconnects.
* **ESP32 Edge Router (The Bridge):**
    * **Protocol Translation:** Acts as an autonomous WiFi ↔ LoRa multi-hop bridge.
    * **Data Aggregation:** Collects telemetry from downstream nodes and routes it to the MQTT control plane.

---

### 2. Edge Compute Layer — Embedded TinyML Engine
ESP32 devices operate as active edge computers running on-device intelligence rather than acting as passive endpoints.

<img width="603" height="670" alt="image" src="https://github.com/user-attachments/assets/ec28dfdd-c892-4907-ac22-1f4b8aa695ff" />
<img width="927" height="433" alt="image" src="https://github.com/user-attachments/assets/d29fb47a-2284-4983-8130-1779867a4211" />


* **ESP32-S3 — Edge AI Vision Node:**
    * **On-Device CNN Inference:** Executes fully quantized **INT8 FOMO / MobileNetV2** models for real-time object detection without cloud dependency.
    * **Hardware Optimization:** Dual-core task separation and optimized DMA camera pipeline to mitigate memory conflicts with the Wi-Fi stack.
    * **Resource-Constrained Efficiency:** Demonstrates high-performance TinyML constrained strictly within MCU hardware limits.



---

### 3. Lightweight Edge Gateway — Raspberry Pi 4B
A self-built, localized gateway stack that replaces heavy industrial IoT frameworks.
<img width="1093" height="564" alt="image" src="https://github.com/user-attachments/assets/077f3ad7-9720-4798-a27f-16268243aef7" />
<img width="1407" height="508" alt="image" src="https://github.com/user-attachments/assets/c41494dc-929a-4762-afcb-992603d1f653" />

* **Core Architecture:** Driven by an asynchronous **FastAPI control plane** and an **MQTT event backbone**.
* **Infrastructure Services:** Manages dynamic device registries, telemetry storage, and the end-to-end **OTA firmware lifecycle**.
* **Design Philosophy:** Lightweight, hackable, and highly portable—built entirely without the overhead of Kubernetes, cloud lock-in, or proprietary SDKs.



---

### 4. Management UI — Web Control Plane
The responsive, high-observability frontend dashboard provides direct human-in-the-loop orchestration over the entire edge network.

<img width="1366" height="715" alt="image" src="https://github.com/user-attachments/assets/b8b42439-cbe4-4a3e-88c8-ad27da3deb60" />
<img width="1282" height="359" alt="image" src="https://github.com/user-attachments/assets/f55dcadb-e209-42dd-aec0-bd8f16b5e9ac" />


* **Unified Monitoring:** Real-time stream visualization of gateway hardware metrics and edge node telemetry.
* **Lifecycle Control:** Centralized interface to trigger remote OTA firmware updates and manage active device deployment registries.



---

## Key Capabilities

### MCU-Level Edge AI
Real-time object detection and inference running locally on ESP32-S3, achieving zero cloud dependency and minimum bandwidth utilization.

### Self-Built Gateway Infrastructure
Custom, hardware-efficient gateway replacing heavy commercial IoT stacks with a lightweight asynchronous backend.

### OTA Device Lifecycle Management
End-to-end remote firmware deployment featuring real-time deployment job tracking, node status monitoring, and binary version control.

### Hybrid Network Topology
A unified network control loop managing WiFi devices, standalone LoRa sensor networks, and multi-hop edge bridges simultaneously.

### Out-of-Band Monitoring
Comprehensive, full-stack health visibility across all layers:
* **Gateway Plane:** CPU / RAM / Core Temperature metrics.
* **Edge Node Plane:** RSSI / SNR / Heartbeat packet verification.


### 🛠️ Engineering Challenges Solved 🛠️
- ESP32 Camera + WiFi DMA Conflict
- Stabilized concurrent camera streaming and WiFi networking through memory tuning and task isolation.
- Long-Range Packet Corruption
- Implemented defensive JSON parsing for unreliable LoRa transmissions.
- Autonomous Device Onboarding
- Dynamic device registry enabling plug-and-deploy nodes.

### Development Roadmap <br>
Phase	Description<br>
- [x] P0-P2	Gateway Core & MQTT Pipeline<br>
- [x] P3	OTA Manager<br>
- [x] P4	MCU Edge AI Deployment<br>
- [x] P5-P6	LoRa Multi-Hop Integration<br>
- [ ] P7	Security Hardening<br>
- [ ] P8	Event Bus & Edge Automation<br>


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

### Author <br>
Angus Ku <br>
2026 Embedded Systems • Edge AI • Distributed IoT Infrastructure 

