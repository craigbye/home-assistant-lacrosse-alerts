import aiohttp
import asyncio
import logging
from datetime import datetime, timezone


_LOGGER = logging.getLogger(__name__)

class SensorClient:
    def __init__(self, base_url: str, sensor_id: str):
        self._base_url = base_url
        self._sensor_id = sensor_id
        self._data = {}
        self._valid = False

    async def update(self):
        """Fetch and parse sensor data from the remote API asynchronously."""
        self._data = {}
        self._valid = False

        url = f"{self._base_url}?deviceid={self._sensor_id}&metric=1"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    raw = await response.json()
        
        except (aiohttp.ClientError, aiohttp.ClientResponseError, asyncio.TimeoutError) as e:
            _LOGGER.error("Request failed for sensor %s: %s", self._sensor_id, e)
            return

        except Exception as e:
            _LOGGER.error("Unexpected error for sensor %s: %s", self._sensor_id, e)
            return

        device_data = raw.get("device0")
        if not device_data:
            _LOGGER.warning("Missing 'device0' in response for sensor %s", self._sensor_id)
            return

        obs_list = device_data.get("obs")
        if not isinstance(obs_list, list) or not obs_list:
            _LOGGER.warning("Missing or invalid 'obs' list for sensor %s", self._sensor_id)
            return

        self._data = obs_list[0]
        self._valid = True


    @property
    def ambient_temperature(self):
        value = self._data.get("ambient_temp")
        return value if isinstance(value, (int, float)) else None
    
    @property
    def probe_temperature(self):
        value = self._data.get("probe_temp")
        return value if isinstance(value, (int, float)) else None

    @property
    def humidity(self):
        value = self._data.get("humidity")
        return value if isinstance(value, (int, float)) else None

    @property
    def low_battery(self):
        return self._data.get("lowbattery") == "1"

    @property
    def water_present(self):
        value = self._data.get("probe_temp")
        if self.device_type != "TX70":
            return None
        elif value == "Dry":
            return False
        elif value == "Wet":
            return True
        elif value == "N/C":
            return None


    @property
    def link_quality(self):
        value = self._data.get("linkquality")
        return value if isinstance(value, int) else None

    @property
    def device_id(self):
        return self._sensor_id
    
    @property
    def api_url(self):
        return self._base_url

    @property
    def device_type(self):
        value = self._data.get("device_type")
        return value if isinstance(value, (str)) else None

    @property
    def is_valid(self):
        """Returns True if the last update was successful and data is usable."""
        return self._valid
    
    @property
    def measured_time(self):
        """Return the UTC datetime of the measurement, or None if invalid."""
        raw_ts = self._data.get("utctime")
        if isinstance(raw_ts, (int, float)):
            try:
                return datetime.fromtimestamp(raw_ts, tz=timezone.utc)

            except (ValueError, OSError) as e:
                _LOGGER.warning("Invalid utctime value: %s", raw_ts)
                return None
        _LOGGER.debug("utctime missing or not numeric: %s", raw_ts)
        return None


    @property
    def all_attributes(self):
        return {
            "ambient temperature": self.ambient_temperature,
            "probe temperature": self.probe_temperature,
            "humidity": self.humidity,
            "low_battery": self.low_battery,
            "water_present": self.water_present,
            "link_quality": self.link_quality,
            "device_type": self.device_type,
            "measured_time": self.measured_time,
        }