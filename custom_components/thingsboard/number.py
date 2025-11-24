"""Number platform for ThingsBoard integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ThingsBoardDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ThingsBoard number entities based on a config entry."""
    coordinator: ThingsBoardDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_numbers() -> None:
        """Add number entities for writable numeric attributes."""
        entities = []

        if coordinator.data:
            for key, value in coordinator.data.items():
                # Only create numbers for shared attributes (controllable)
                # and only if they are numeric
                if key.startswith("shared_") and isinstance(value, (int, float)):
                    entity_id = f"number.thingsboard_{key}"

                    # Check if entity already exists
                    if entity_id not in [
                        entity.entity_id
                        for entity in hass.data[DOMAIN].get("number_entities", [])
                    ]:
                        entities.append(
                            ThingsBoardNumber(
                                coordinator=coordinator,
                                entry=entry,
                                attribute_key=key,
                            )
                        )

        if entities:
            # Store entities for tracking
            if "number_entities" not in hass.data[DOMAIN]:
                hass.data[DOMAIN]["number_entities"] = []
            hass.data[DOMAIN]["number_entities"].extend(entities)

            async_add_entities(entities)

    # Initial setup
    async_add_numbers()

    # Listen for coordinator updates to add new entities
    entry.async_on_unload(coordinator.async_add_listener(async_add_numbers))


class ThingsBoardNumber(CoordinatorEntity, NumberEntity):
    """Representation of a ThingsBoard Number entity."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: ThingsBoardDataUpdateCoordinator,
        entry: ConfigEntry,
        attribute_key: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)

        self._attribute_key = attribute_key
        self._entry = entry

        # Remove 'shared_' prefix for display
        display_name = attribute_key.replace("shared_", "")

        # Create unique ID
        self._attr_unique_id = f"{entry.entry_id}_{attribute_key}_number"

        # Set name
        self._attr_name = f"ThingsBoard {display_name.replace('_', ' ').title()}"

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="ThingsBoard Device",
            manufacturer="ThingsBoard",
            model="HTTP API Device",
            configuration_url=coordinator.host,
        )

        # Set reasonable defaults for min/max
        self._attr_native_min_value = -1000000
        self._attr_native_max_value = 1000000
        self._attr_native_step = 0.1

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data:
            value = self.coordinator.data.get(self._attribute_key)
            if isinstance(value, (int, float)):
                return float(value)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        # Extract the actual attribute name (without 'shared_' prefix)
        attribute_name = self._attribute_key.replace("shared_", "")

        # Set the attribute on ThingsBoard
        success = await self.coordinator.async_set_shared_attributes(
            {attribute_name: value}
        )

        if success:
            _LOGGER.debug("Successfully set %s to %s", attribute_name, value)
        else:
            _LOGGER.error("Failed to set %s to %s", attribute_name, value)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self._attribute_key in self.coordinator.data
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        return {
            "attribute_key": self._attribute_key,
            "last_update": self.coordinator.last_update_success_time,
        }
