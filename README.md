# 📡 LaCrosse Alerts Integration for Home Assistant

This custom integration connects your [LaCrosse Alerts](https://lacrossealertsmobile.com/) devices to Home Assistant using cloud polling. It supports multiple devices and provides sensor data directly in your dashboard.

Tested with:
- ✅ TX60
- ✅ TX70

---

## 🚀 Features

- Cloud polling of LaCrosse Alerts sensor data  
- Support for multiple devices  
- Setup entirely via the Home Assistant UI  
- Sensor entities for temperature, humidity, and wet/dry (depending on sensor model)

---

## 📦 Installation

### Option 1: HACS (Recommended)
1. Go to **HACS > Integrations**
2. Click the three-dot menu (`⋮`) > **Custom repositories**
3. Add your repository URL and select **Integration** as category
4. Search for "LaCrosse Alerts" and install
5. Restart Home Assistant

### Option 2: Manual
1. Clone this repository into your `custom_components` folder:
   ```bash 
   git clone https://github.com/craigbye/home-assistant-lacrosse-alerts.git custom_components/lacrosse_alerts
2. Restart Home Assistant

---

## ⚙️ Configuration
Configuration is done entirely through the Home Assistant UI:
1. Go to Settings > Devices & Services
2. Click Add Integration
3. Search for LaCrosse Alerts
4. Enter the following for each device:
5. Device Name: A friendly name for your sensor
6. Device ID: The 16-digit ID from your LaCrosse Alerts unit
You can add multiple devices by repeating the setup process.

---

## 🧪 Device Compatibility
Currently tested with:
- TX60
- TX70
Other models may work but are unverified. Feel free to report compatibility or issues via GitHub.

---

## 🛠️ Troubleshooting
- Double-check your 16-digit device ID
- Ensure your device is active and reporting to [LaCrosse Alerts](https://lacrossealertsmobile.com/)
- Restart Home Assistant after installation
- Check logs under Settings > System > Logs for errors

---

## 🙋‍♂️ Support & Contributions
Found a bug or want to request a feature? Open an issue or submit a pull request.

---

📄 License
This project is licensed under the MIT License. See the LICENSE file for details

---

