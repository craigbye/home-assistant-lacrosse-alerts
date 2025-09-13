"""The La Crosse Alerts Sensors integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .lacrosse_sensor_client import SensorClient


# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.SENSOR]

# TODO Create ConfigEntry type alias with API object
# Rename type alias and update all entry annotations
type LaCrosseConfigEntry = ConfigEntry[SensorClient]



# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: LaCrosseConfigEntry) -> bool:
    """Set up La Crosse Alerts Sensors from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    api_key = entry.data["api_key"]
    client = SensorClient(
        "https://decent-destiny-704.appspot.com/laxservices/device_info.php",
        api_key,
    )

    entry.runtime_data = client
    
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: LaCrosseConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
