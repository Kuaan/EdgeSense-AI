# EdgeSense-AI
**MCU-Scale Edge AI & Device Orchestration Platform**

A lightweight edge computing platform built on ESP32-class microcontrollers — proving that distributed edge infrastructure doesn't require powerful hardware or cloud dependency.
---
## Stack
`ESP32-S3` `STM32F103` `Raspberry Pi 4B` `FreeRTOS` `TinyML` `FastAPI` `MQTT` `LoRa` `OTA`
---
## Core Idea

> Microcontrollers act as real edge computers instead of simple sensor nodes.

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
        │                     │                     │
 ┌──────▼────────┐    ┌───────▼───────┐     ┌───────▼───────┐
 │ ESP32-S3      │    │ ESP32 Node    │     │ ESP32 Node    │
 │ Edge AI       │    │ Edge Router   │     │      or       │ 
 │ Vision Compute│    │ LoRa Gateway  │     │ Future Nodes  │
 └───────────────┘    └───────┬───────┘     └───────────────┘
                              │ LoRa
                      ┌───────▼───────┐
                      │ STM32 Sensor  │
                      │ Deep Edge     │
                      └───────────────┘
```
| Layer | Hardware | Role |
|---|---|---|
| Deep Edge | STM32F103 + FreeRTOS | LoRa telemetry, fail-safe autonomous operation |
| Edge Compute | ESP32-S3 | INT8 FOMO / MobileNetV2 on-device inference |
| Gateway | Raspberry Pi 4B | FastAPI + MQTT control plane, OTA lifecycle |
| Management UI | Web | Real-time dashboard, remote OTA, device registry |

---

## Key Engineering Challenges

| Challenge | Solution |
|---|---|
| ESP32 Camera + WiFi DMA conflict | Memory tuning + dual-core task isolation |
| LoRa packet corruption over long range | Defensive JSON parsing for unreliable links |
| Dynamic device onboarding | Plug-and-deploy registry with auto-registration |

---

## Status

| Phase | Feature | Status |
|---|---|---|
| P0–P3 | Gateway Core, MQTT Pipeline, OTA Manager | ✅ |
| P4 | MCU Edge AI Deployment | ✅ |
| P5–P6 | LoRa Multi-Hop Integration | ✅ |
| P7 | Security Hardening | 🔲 |
| P8 | Event Bus & Edge Automation | 🔲 |

---

## Quick Start

```bash
git clone https://github.com/Kuaan/EdgeSense-AI.git
cd EdgeSense-AI/gateway
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Firmware binaries: `/firmware`

---

---

## System Detail

### Layer 1 — Deep Edge: LoRa Sensor Topology

Extends operational visibility into low-bandwidth, non-IP field environments.

**STM32F103 (Endpoint)**
- FreeRTOS for deterministic, time-critical sensor sampling
- Low-overhead LoRa transmission optimized for unstable links
- Operates autonomously at field perimeter even during backhaul disconnects

**ESP32 Edge Router (Bridge)**
- Autonomous WiFi ↔ LoRa multi-hop protocol translation
- Aggregates downstream telemetry and routes to MQTT control plane

---

### Layer 2 — Edge Compute: Embedded TinyML Engine

ESP32-S3 operates as an active edge computer running on-device intelligence, not a passive sensor endpoint.

<img width="603" height="670" alt="image" src="https://github.com/user-attachments/assets/ec28dfdd-c892-4907-ac22-1f4b8aa695ff" />
<img width="603" height="288" alt="image" src="https://github.com/user-attachments/assets/d29fb47a-2284-4983-8130-1779867a4211" />

- **On-Device CNN Inference:** Fully quantized INT8 FOMO / MobileNetV2 for real-time object detection, zero cloud dependency
- **Hardware Optimization:** Dual-core task separation + optimized DMA camera pipeline to eliminate WiFi stack memory conflicts
- **Resource-Constrained Efficiency:** High-performance TinyML within strict MCU hardware limits

---

### Layer 3 — Gateway: Raspberry Pi 4B

Self-built localized gateway stack replacing heavy industrial IoT frameworks — no Kubernetes, no cloud lock-in, no proprietary SDKs.

<img width="1093" height="564" alt="image" src="https://github.com/user-attachments/assets/077f3ad7-9720-4798-a27f-16268243aef7" />
<img width="1407" height="508" alt="image" src="https://github.com/user-attachments/assets/c41494dc-929a-4762-afcb-992603d1f653" />

- **Control Plane:** Asynchronous FastAPI backend + MQTT event backbone
- **Infrastructure Services:** Dynamic device registry, telemetry storage, end-to-end OTA firmware lifecycle
- **Out-of-Band Monitoring:** CPU / RAM / Core Temperature (gateway) · RSSI / SNR / Heartbeat (edge nodes)

---

### Layer 4 — Management UI: Web Control Plane

Responsive dashboard for human-in-the-loop orchestration over the entire edge network.

<img width="1366" height="715" alt="image" src="https://github.com/user-attachments/assets/b8b42439-cbe4-4a3e-88c8-ad27da3deb60" />
<img width="1282" height="359" alt="image" src="https://github.com/user-attachments/assets/f55dcadb-e209-42dd-aec0-bd8f16b5e9ac" />

- **Unified Monitoring:** Real-time gateway hardware metrics and edge node telemetry streams
- **Lifecycle Control:** Remote OTA firmware triggers and active device deployment registry

---

**Angus Ku** · Embedded Systems · Edge AI · Distributed IoT Infrastructure · 2026
