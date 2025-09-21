"""Support for LaCrosse Alerts sensor components."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging

from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_DEVICE,
    CONF_ID,
    CONF_NAME,
    CONF_SENSORS,
    CONF_TYPE,
    EVENT_HOMEASSISTANT_STOP,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt as dt_util
from homeassistant.helpers.typing import StateType

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import STATE_ON, STATE_OFF


from .lacrosse_sensor_client import SensorClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

TYPES = ["battery", "humidity", "temperature"]
LACROSSE_URL = "http://decent-destiny-704.appspot.com/laxservices/device_info.php"


from . import LaCrosseConfigEntry

async def async_setup_entry(
    hass: HomeAssistant,
    entry: LaCrosseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    
    client = entry.runtime_data  # This is now typed as SensorClient

    # Fetch initial data to determine model
    await client.update()  

    # Create set of sensors for this client
    entities = [
        LaCrosseTemperature(client, entry.data["name"]),
        LaCrosseHumidity(client, entry.data["name"]),
        LaCrosseBattery(client, entry.data["name"]),
        LaCrosseLinkQuality(client, entry.data["name"]),
        LaCrosseTimestampSensor(client, entry.data["name"]),
    ]

    if client.device_type == "TX70":
        entities.append(LaCrosseWaterSensor(client, entry.data["name"]))

    if client.device_type == "TX60":
        entities.append(LaCrosseProbeTemperature(client, entry.data["name"]))
    

    async_add_entities(entities)


class BaseLaCrosseSensor(SensorEntity):
    """Base class for LaCrosse sensor entities."""

    def __init__(self, client: SensorClient, device_name: str, unique_suffix: str):
        self._client = client
        self._attr_should_poll = True
        self._device_name = device_name
        self._device_id = client.device_id
        self._attr_name = f"{device_name} {unique_suffix.capitalize()}"
        self._attr_unique_id = f"{client._sensor_id}_{unique_suffix}"
        self._attr_extra_state_attributes = {}

    async def async_update(self) -> None:
        """Fetch new data from the API."""
        await self._client.update()
        _LOGGER.info("Polling sensor %s", self._client.device_id)
        _LOGGER.info("Attributes: %s", self._client.all_attributes)
        self._attr_extra_state_attributes = self._client.all_attributes

    async def async_added_to_hass(self):
        """Run when entity is added to Home Assistant."""
        await self.async_update()


    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._client.device_id)},
            "name": f"LaCrosse Sensor {self._client.device_type}",
            "manufacturer": "LaCrosse Technology",
            "model": self._client.device_type or "Unknown",
            "configuration_url": f"{self._client._base_url}",
    }


class LaCrosseTemperature(BaseLaCrosseSensor):
    """Ambient temperature sensor."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = "temperature"
    _attr_state_class = "measurement"

    def __init__(self, client: SensorClient, device_name: str):
        super().__init__(client, device_name, "ambient temperature")


    @property
    def native_value(self) -> StateType:
        return self._client.ambient_temperature
    
class LaCrosseProbeTemperature(BaseLaCrosseSensor):
    """Probe temperature sensor."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = "temperature"
    _attr_state_class = "measurement"

    def __init__(self, client: SensorClient, device_name: str):
        super().__init__(client, device_name, "probe temperature")


    @property
    def native_value(self) -> StateType:
        return self._client.probe_temperature


class LaCrosseLinkQuality(BaseLaCrosseSensor):
    """Link Quality sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = "signal_strength"
    _attr_state_class = "measurement"

    def __init__(self, client: SensorClient, device_name: str):
        super().__init__(client, device_name, "link quality")


    @property
    def native_value(self) -> StateType:
        return self._client.link_quality

class LaCrosseTimestampSensor(BaseLaCrosseSensor):


    _attr_device_class = "timestamp"
    _attr_state_class = "measurement"

    def __init__(self, client: SensorClient, device_name: str):
        super().__init__(client, device_name, "sensor timestamp")

    @property
    def native_value(self):
        # Return the timestamp as a datetime object (UTC or local)
        return dt_util.as_local(self._client.measured_time)


class LaCrosseHumidity(BaseLaCrosseSensor):
    """Humidity sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = "humidity"
    _attr_state_class = "measurement"

    def __init__(self, client: SensorClient, device_name: str):
        super().__init__(client, device_name, "humidity")


    @property
    def native_value(self) -> StateType:
        return self._client.humidity


class LaCrosseBattery(BaseLaCrosseSensor):
    """Battery status sensor."""

    def __init__(self, client: SensorClient, device_name: str):
        super().__init__(client, device_name, "battery")


    @property
    def native_value(self) -> StateType:
        if self._client.low_battery is None:
            return None
        return "low" if self._client.low_battery else "ok"

    @property
    def icon(self) -> str:
        if self._client.low_battery is None:
            return "mdi:battery-unknown"
        return "mdi:battery-alert" if self._client.low_battery else "mdi:battery"


class LaCrosseWaterSensor(BinarySensorEntity):
    """Binary sensor for wet/dry detection."""

    def __init__(self, client: SensorClient, device_name: str):

        self._client = client
        self._attr_should_poll = True
        self._device_name = device_name
        self._device_id = client.device_id
        self._attr_name = f"{device_name} Water"
        self._attr_unique_id = f"{client._sensor_id}_water"
        self._attr_extra_state_attributes = {}

        self._attr_device_class = "moisture"

    async def async_update(self):
        await self._client.update()

    @property
    def is_on(self) -> bool | None:
        """Return True if water is present, False if dry, None if unknown."""
        return self._client.water_present

    
    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._client.device_id)},
            "name": f"LaCrosse Sensor {self._client.device_type}",
            "manufacturer": "LaCrosse Technology",
            "model": self._client.device_type or "Unknown",
            "configuration_url": f"{self._client._base_url}",
    }

