"""Switch platform for Anker Solix F2000 Bluetooth integration.

This module exposes switch entities to control AC outlets, DC outlets, and Power Saving Mode.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AnkerSolixBluetoothUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SWITCH_DESCRIPTIONS: list[SwitchEntityDescription] = [
    SwitchEntityDescription(
        key="ac_outlet_on",
        name="AC Sockets Master",
        icon="mdi:power-socket-us",
    ),
    SwitchEntityDescription(
        key="twelve_volt_on",
        name="12V Car Port Master",
        icon="mdi:car-electric",
    ),
    SwitchEntityDescription(
        key="power_save_on",
        name="Power Saving Mode",
        icon="mdi:sprout",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Anker Solix F2000 switch entities from ConfigEntry."""
    coordinator: AnkerSolixBluetoothUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        AnkerSolixSwitch(coordinator, desc)
        for desc in SWITCH_DESCRIPTIONS
    ]
    async_add_entities(switches)


class AnkerSolixSwitch(
    CoordinatorEntity[AnkerSolixBluetoothUpdateCoordinator],
    SwitchEntity,
):
    """Representation of an Anker Solix toggle switch control."""

    def __init__(
        self,
        coordinator: AnkerSolixBluetoothUpdateCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch entity."""
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
    def is_on(self) -> bool | None:
        """Return true if the switch setting state is active."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return bool(value)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the control switch ON."""
        cmd_id = self._get_command_id()
        _LOGGER.debug("Turning switch %s ON via BLE", self.entity_description.key)
        await self.coordinator.async_send_control_command(cmd_id, bytes([0x01]))

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the control switch OFF."""
        cmd_id = self._get_command_id()
        _LOGGER.debug("Turning switch %s OFF via BLE", self.entity_description.key)
        await self.coordinator.async_send_control_command(cmd_id, bytes([0x00]))

    def _get_command_id(self) -> int:
        """Map entity key to unencrypted control command ID."""
        key = self.entity_description.key
        if key == "ac_outlet_on":
            return 0x86
        if key == "twelve_volt_on":
            return 0x87
        if key == "power_save_on":
            return 0x8A
        raise ValueError(f"Unknown switch command key: {key}")
