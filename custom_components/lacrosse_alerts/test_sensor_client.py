import logging
import asyncio
from lacrosse_sensor_client import SensorClient

# Optional: configure logging to see debug output
logging.basicConfig(level=logging.INFO)

async def main():
    
    test_url = "https://decent-destiny-704.appspot.com/laxservices/device_info.php"
    # Replace with your sensor ID
    test_id = "0000000000000000"

    client = SensorClient(test_url, test_id)
    await client.update()

    if client.is_valid:
        print("✅ Sensor data fetched successfully:")
        print(f"Ambient Temperature: {client.ambient_temperature} °C")
        print(f"Probe Temperature: {client.probe_temperature} °C")
        print(f"Humidity: {client.humidity} %")
        print(f"Low Battery: {'Yes' if client.low_battery else 'No'}")
        print(f"Water Present: {'Yes' if client.water_present else 'No'}")
        print(f"Link Quality: {client.link_quality} %")
        print(f"Device Type: {client.device_type}")
        print(f"Measured Time: {client.measured_time}")
        print(f"All Attributes: {client.all_attributes}")
    else:
        print("❌ Failed to fetch or parse sensor data.")

if __name__ == "__main__":
    asyncio.run(main())