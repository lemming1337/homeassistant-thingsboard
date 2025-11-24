"""Sensor platform for ThingsBoard integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
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
    """Set up ThingsBoard sensor based on a config entry."""
    coordinator: ThingsBoardDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_sensors() -> None:
        """Add sensors based on coordinator data."""
        entities = []

        # Create a sensor for each attribute discovered
        if coordinator.data:
            for key, value in coordinator.data.items():
                # Skip if entity already exists
                entity_id = f"sensor.thingsboard_{key}"
                if entity_id not in [
                    entity.entity_id for entity in hass.data[DOMAIN].get("entities", [])
                ]:
                    entities.append(
                        ThingsBoardSensor(
                            coordinator=coordinator,
                            entry=entry,
                            attribute_key=key,
                        )
                    )

        if entities:
            # Store entities for tracking
            if "entities" not in hass.data[DOMAIN]:
                hass.data[DOMAIN]["entities"] = []
            hass.data[DOMAIN]["entities"].extend(entities)

            async_add_entities(entities)

    # Initial setup
    async_add_sensors()

    # Listen for coordinator updates to add new entities
    entry.async_on_unload(coordinator.async_add_listener(async_add_sensors))


class ThingsBoardSensor(CoordinatorEntity, SensorEntity):
    """Representation of a ThingsBoard Sensor."""

    def __init__(
        self,
        coordinator: ThingsBoardDataUpdateCoordinator,
        entry: ConfigEntry,
        attribute_key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._attribute_key = attribute_key
        self._entry = entry

        # Create unique ID
        self._attr_unique_id = f"{entry.entry_id}_{attribute_key}"

        # Set name
        self._attr_name = f"ThingsBoard {attribute_key.replace('_', ' ').title()}"

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="ThingsBoard Device",
            manufacturer="ThingsBoard",
            model="HTTP API Device",
            configuration_url=coordinator.host,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._attribute_key)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        return {
            "attribute_key": self._attribute_key,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self._attribute_key in self.coordinator.data
        )

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return the state class of this sensor."""
        # Try to determine if the value is numeric
        if self.coordinator.data:
            value = self.coordinator.data.get(self._attribute_key)
            if isinstance(value, (int, float)):
                return SensorStateClass.MEASUREMENT
        return None
