"""Number platform for Anker Solix F2000 Bluetooth integration.

This module exposes number entities to configure the AC Recharging Power limit.
"""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AnkerSolixBluetoothUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

NUMBER_DESCRIPTIONS: list[NumberEntityDescription] = [
    NumberEntityDescription(
        key="ac_recharging_power",
        name="AC Recharging Power Limit",
        native_min_value=200.0,
        native_max_value=2200.0,
        native_step=100.0,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:lightning-bolt",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Anker Solix F2000 number entities from ConfigEntry."""
    coordinator: AnkerSolixBluetoothUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    numbers = [
        AnkerSolixNumber(coordinator, desc)
        for desc in NUMBER_DESCRIPTIONS
    ]
    async_add_entities(numbers)


class AnkerSolixNumber(
    CoordinatorEntity[AnkerSolixBluetoothUpdateCoordinator],
    NumberEntity,
):
    """Representation of an Anker Solix numeric configuration slider control."""

    def __init__(
        self,
        coordinator: AnkerSolixBluetoothUpdateCoordinator,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device.address}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device.address)},
            name=coordinator.device_name,
            manufacturer="Anker",
            model="Solix F2000 (767 PowerHouse)",
        )

    @property
    def native_value(self) -> float | None:
        """Return the current active configuration limit."""
        if self.coordinator.data is None:
            return None
        val = self.coordinator.data.get(self.entity_description.key)
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the F2000 recharging power limit configuration to the chosen value."""
        key = self.entity_description.key
        if key == "ac_recharging_power":
            cmd_id = 0x80
            watts = int(value)
            payload = watts.to_bytes(2, byteorder="little")
            _LOGGER.debug("Setting AC Recharging Power Limit to %dW via BLE", watts)
            await self.coordinator.async_send_control_command(cmd_id, payload)
