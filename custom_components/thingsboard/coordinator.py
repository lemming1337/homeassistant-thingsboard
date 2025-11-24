"""DataUpdateCoordinator for ThingsBoard."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_ACCESS_TOKEN, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ThingsBoardDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching ThingsBoard data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.host = entry.data[CONF_HOST]
        self.token = entry.data[CONF_ACCESS_TOKEN]
        self.session = async_get_clientsession(hass)
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from ThingsBoard.

        This method fetches both client-side and shared attributes.
        The attributes are used to discover entities dynamically.
        """
        try:
            # Fetch all attributes (both client and shared)
            url = f"{self.host}/api/v1/{self.token}/attributes"

            async with self.session.get(
                url, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 401:
                    raise UpdateFailed("Invalid access token")
                elif response.status != 200:
                    raise UpdateFailed(f"Error fetching data: HTTP {response.status}")

                data = await response.json()

                # ThingsBoard returns attributes in the format:
                # {
                #   "client": {...},
                #   "shared": {...}
                # }

                # Flatten the structure for easier access
                flattened_data = {}

                if "client" in data:
                    for key, value in data["client"].items():
                        flattened_data[f"client_{key}"] = value

                if "shared" in data:
                    for key, value in data["shared"].items():
                        flattened_data[f"shared_{key}"] = value

                # Also try to fetch latest telemetry if available
                # Note: The standard HTTP API doesn't provide a way to fetch
                # latest telemetry directly. This would require the REST API
                # with proper authentication. For now, we focus on attributes.

                _LOGGER.debug("Fetched ThingsBoard data: %s", flattened_data)

                return flattened_data

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def async_set_shared_attributes(self, attributes: dict[str, Any]) -> bool:
        """Set shared attributes on ThingsBoard device.

        Args:
            attributes: Dictionary of attributes to set (e.g., {"temperature": 22.5})

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.host}/api/v1/{self.token}/attributes"

            async with self.session.post(
                url,
                json=attributes,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 401:
                    _LOGGER.error("Invalid access token when setting attributes")
                    return False
                elif response.status not in (200, 201):
                    _LOGGER.error("Error setting attributes: HTTP %s", response.status)
                    return False

                _LOGGER.info("Successfully set attributes: %s", attributes)
                # Trigger an immediate refresh to update the entities
                await self.async_request_refresh()
                return True

        except aiohttp.ClientError as err:
            _LOGGER.error("Error communicating with API: %s", err)
            return False
        except Exception as err:
            _LOGGER.exception("Unexpected error setting attributes: %s", err)
            return False
