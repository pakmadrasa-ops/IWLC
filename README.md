# Intelligent Water Level Controller

**ESP8266 + MicroPython | Local + Wireless Control | Fail-Safe Design**

An **intelligent, Wi-Fi–enabled water level controller** built on **ESP8266** using **MicroPython**.
Designed for **homes, mosques, schools, and small buildings**, this system automatically manages a water pump based on tank levels. Ensures **reliability even when the internet is down**.

---

## Key Features

*   **Automatic Pump Control**
  Starts and stops the water pump based on tank level sensors and utility water availability.

*   **ESP8266 + MicroPython**
  Lightweight and readable firm with Over-The-Air (OTA) updates provisioning.

*  **Built-in Web Interface**
  Control the pump from any browser (mobile or desktop).

*  **Fail-Safe Operation**

  * Pump logic continues working even if Wi-Fi disconnects
  * Stored configuration survives reboot and power loss

*   **Manual Override**
  Physical switch for emergency control.

*   **OTA Firmware Update (Wireless)**
  Update firmware remotely with rollback safety.

*  **Offline First Design**
  Local control works without cloud dependency.

---

##  How It Works (High Level)

1. **Level Sensors** detect water level (LOW / FULL)
2. **Current Sensors** detect pump dry run (current is proportion to water flow)
3. **ESP8266** runs control logic in MicroPython
4. **Relay Module** switches the pump ON or OFF
5. **Web Server** allows:

   * Pump control
   * Status monitoring
   * Configuration
6. **Fail-safe logic** prevents:

   * Dry running
   * Rapid ON/OFF cycling
   * Corruption during failed updates

---

##  Hardware Requirements

* ESP8266 (NodeMCU / ESP-12 / ESP-01 with relay board)
* Relay module (optically isolated preferred)
* Water level sensors (float sensors)
* Power supply (stable 5V / 3.3V as required)
* Optional: manual switch, status LED

---

##  Software Stack

* **MicroPython (ESP8266 build)**
* Built-in modules:

  * `network`
  * `socket`
  * `machine`
  * `ujson`
  * `uos`
* No cloud lock-in

---

## 🌍 Network & Control Modes

| Mode                 | Works Without Internet | Description               |
| -------------------- | ---------------------- | ------------------------- |
| Automatic            | ✅                      | Sensor-based pump control |
| Web UI (LAN)         | ✅                      | Local browser control     |
| Access Point (Setup) | ✅                      | First-time Wi-Fi setup    |
| OTA Update           | ❌ (LAN required)       | Wireless firmware updates |

---

## Safety & Reliability

* Stored configuration in flash (JSON)
* Watchdog-friendly logic
* Debounced sensor readings
* Pump delay to protect motor
* OTA update with fallback protection

---

##  Getting Started

1. Flash **MicroPython** on ESP8266
2. Upload project files using:

   * Thonny
   * mpremote
   * rshell
3. Power the device
4. Connect to setup Wi-Fi AP
5. Open browser → configure → done ✅

---

## Intended Use Cases

* Overhead tank automation
* Underground tank protection
* Water pump dry-run prevention
* Smart home water management
* Low-cost IoT education projects

---

##  License

This project is released under the **MIT License** —
free to use, modify, and deploy in personal or commercial products.

---

##  Contributions

Pull requests, bug reports, and improvements are welcome.
Keep the project **simple, reliable, and offline-friendly**.

---


