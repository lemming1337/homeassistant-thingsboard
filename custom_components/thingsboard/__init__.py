"""The ThingsBoard integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import ThingsBoardDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER]

# Service schemas
SERVICE_SET_ATTRIBUTE = "set_attribute"
SERVICE_SET_ATTRIBUTES = "set_attributes"

SERVICE_SET_ATTRIBUTE_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry_id"): cv.string,
        vol.Required("attribute_key"): cv.string,
        vol.Required("value"): vol.Any(str, int, float, bool),
    }
)

SERVICE_SET_ATTRIBUTES_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry_id"): cv.string,
        vol.Required("attributes"): dict,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ThingsBoard from a config entry."""
    coordinator = ThingsBoardDataUpdateCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_set_attribute(call: ServiceCall) -> None:
        """Handle the set_attribute service call."""
        config_entry_id = call.data["config_entry_id"]
        attribute_key = call.data["attribute_key"]
        value = call.data["value"]

        if config_entry_id not in hass.data[DOMAIN]:
            _LOGGER.error("Config entry %s not found", config_entry_id)
            return

        coordinator: ThingsBoardDataUpdateCoordinator = hass.data[DOMAIN][
            config_entry_id
        ]
        await coordinator.async_set_shared_attributes({attribute_key: value})

    async def handle_set_attributes(call: ServiceCall) -> None:
        """Handle the set_attributes service call."""
        config_entry_id = call.data["config_entry_id"]
        attributes = call.data["attributes"]

        if config_entry_id not in hass.data[DOMAIN]:
            _LOGGER.error("Config entry %s not found", config_entry_id)
            return

        coordinator: ThingsBoardDataUpdateCoordinator = hass.data[DOMAIN][
            config_entry_id
        ]
        await coordinator.async_set_shared_attributes(attributes)

    # Register services only once for the domain
    if not hass.services.has_service(DOMAIN, SERVICE_SET_ATTRIBUTE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_ATTRIBUTE,
            handle_set_attribute,
            schema=SERVICE_SET_ATTRIBUTE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_ATTRIBUTES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_ATTRIBUTES,
            handle_set_attributes,
            schema=SERVICE_SET_ATTRIBUTES_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
