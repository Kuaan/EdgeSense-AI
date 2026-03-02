🛰️ EdgeSense-AI <br>



Intelligent Secure Edge Device Management System<br>
(Edge AI · BMC-style Management · FreeRTOS · Multi-Protocol Communication · Cybersecurity · OTA)

📌 Phase 0<br>
Raspberry Pi 4B <br>
├── FastAPI (Device Management API)<br>
├── Device Registry (in-memory → SQLite)<br>
├── System Info (CPU / RAM / Disk)<br>
├── Web UI (simply HTML)<br>
└── GitHub-ready project structure<br>
 

📌 Phase 1
 pass;
 
📌 Phase 2
 pass;
 
📌 Phase 3<br>
 Gateway<br>
 ├─ POST /ota/jobs            (establish OTA task)<br>
 ├─ GET  /ota/firmware/{ver}  (ESP32 download bin)<br>
 └─ MQTT publish:<br>
      devices/{id}/ota<br>

ESP32<br>
 ├─ subscribe devices/{id}/ota<br>
 ├─ receive → HTTP GET firmware<br>
 ├─ OTA<br>
 └─ MQTT report<br>


📌 Phase 4
 pass;

📌 Phase 5
 pass;



📜 License

MIT License

🙌 Author

EdgeSense-AI — by Angus Ku (2025)
PRs and Issues are welcome!
