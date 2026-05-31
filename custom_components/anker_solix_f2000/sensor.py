"""Sensor platform for Anker Solix F2000 Bluetooth integration.

This module defines standard numeric sensor entities (Battery %, Temperatures, Input/Output Watts,
and Duration timers) mapping them to appropriate Home Assistant DeviceClasses and unit systems.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AnkerSolixBluetoothUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# List of all numeric sensors exposed by the F2000 BLE API
SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    # Battery Metrics
    SensorEntityDescription(
        key="total_pct",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="internal_pct",
        name="Internal Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="external_pct",
        name="External Battery Expansion",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="battery_state",
        name="Battery Operating State",
        icon="mdi:battery-heart-variant",
    ),
    SensorEntityDescription(
        key="battery_remaining_minutes",
        name="Battery Runtime Remaining",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="internal_temp_c",
        name="Internal Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="external_temp_c",
        name="External Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Power Input Metrics
    SensorEntityDescription(
        key="ac_input_w",
        name="AC Input Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="solar_input_w",
        name="Solar Input Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="total_input_w",
        name="Total Input Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Power Output Metrics
    SensorEntityDescription(
        key="ac_outlet_w",
        name="AC Outlet Power Output",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="total_output_w",
        name="Total Output Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # USB Port Loads
    SensorEntityDescription(
        key="usb_c1_w",
        name="USB-C Port 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="usb_c2_w",
        name="USB-C Port 2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="usb_c3_w",
        name="USB-C Port 3 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="usb_a1_w",
        name="USB-A Port 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="usb_a2_w",
        name="USB-A Port 2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # 12V DC Port Loads
    SensorEntityDescription(
        key="dc_12v_port1_w",
        name="12V Car Port 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dc_12v_port1_timer",
        name="12V Car Port Timer Remaining",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="ac_outlet_timer",
        name="AC Sockets Timer Remaining",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dc_12v_port2_w",
        name="12V Car Port 2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Anker Solix F2000 sensor entities from ConfigEntry."""
    coordinator: AnkerSolixBluetoothUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Dynamically build and add sensors
    sensors = [
        AnkerSolixSensor(coordinator, desc)
        for desc in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(sensors)


class AnkerSolixSensor(
    CoordinatorEntity[AnkerSolixBluetoothUpdateCoordinator],
    SensorEntity,
):
    """Representation of an Anker Solix numeric telemetry sensor."""

    def __init__(
        self,
        coordinator: AnkerSolixBluetoothUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
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
    def native_value(self) -> Any:
        """Return the current telemetry value parsed from the BLE notification stream."""
        if self.coordinator.data is None:
            return None

        # Smart fallback for primary Battery sensor
        if self.entity_description.key == "total_pct":
            ext_connected = self.coordinator.data.get("external_pct") is not None
            if not ext_connected:
                return self.coordinator.data.get("internal_pct")

        return self.coordinator.data.get(self.entity_description.key)
