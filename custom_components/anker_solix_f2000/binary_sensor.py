"""Binary sensor platform for Anker Solix F2000 Bluetooth integration.

This module defines read-only binary status sensor entities (such as AC/DC master outlets,
Power Save status, and individual USB/DC port toggle states) from F2000 telemetry callbacks.
"""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AnkerSolixBluetoothUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# List of all binary sensors exposed by the F2000 BLE API
BINARY_SENSOR_DESCRIPTIONS: list[BinarySensorEntityDescription] = [
    # USB Port States
    BinarySensorEntityDescription(
        key="usb_c1_on",
        name="USB-C Port 1 Active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="usb_c2_on",
        name="USB-C Port 2 Active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="usb_c3_on",
        name="USB-C Port 3 Active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="usb_a1_on",
        name="USB-A Port 1 Active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="usb_a2_on",
        name="USB-A Port 2 Active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    # 12V DC Port States
    BinarySensorEntityDescription(
        key="dc_12v_port1_on",
        name="12V Car Port 1 Active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="dc_12v_port2_on",
        name="12V Car Port 2 Active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Anker Solix F2000 binary sensor entities from ConfigEntry."""
    coordinator: AnkerSolixBluetoothUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Dynamically build and add binary sensors
    binary_sensors = [
        AnkerSolixBinarySensor(coordinator, desc)
        for desc in BINARY_SENSOR_DESCRIPTIONS
    ]
    async_add_entities(binary_sensors)


class AnkerSolixBinarySensor(
    CoordinatorEntity[AnkerSolixBluetoothUpdateCoordinator],
    BinarySensorEntity,
):
    """Representation of an Anker Solix active status binary sensor."""

    def __init__(
        self,
        coordinator: AnkerSolixBluetoothUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device.address}_{description.key}"

        # Standard DeviceInfo linking the entity with the F2000 device instance
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device.address)},
            name=coordinator.device_name,
            manufacturer="Anker",
            model="Solix F2000 (767 PowerHouse)",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor state key is active."""
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        return bool(value)
