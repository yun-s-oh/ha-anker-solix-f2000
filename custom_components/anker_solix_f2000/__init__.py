"""Setup and platform forwarding configurations for the Anker Solix F2000 integration.

This module initializes the custom component instance when loaded from config entries,
resolves active system Bluetooth adapters, mounts the shared telemetry coordinator, and
tears down BLE radio clients during integration unloading.
"""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import AnkerSolixBluetoothUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anker Solix F2000 from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    name: str = entry.data[CONF_NAME]

    _LOGGER.debug("Setting up Anker Solix F2000 entry for %s (%s)", name, address)

    # Resolve physical BLEDevice from the central HA Bluetooth subsystem
    ble_device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find connectable BLE device at address: {address}. "
            "Will retry setup automatically when the device is discovered."
        )

    # Initialize and startup the long-lived BLE coordinator
    coordinator = AnkerSolixBluetoothUpdateCoordinator(hass, entry, ble_device, name)
    await coordinator.async_start()

    # Store coordinator instance globally inside HASS context
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Register options update listener to handle dynamic poll rate changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Forward entry setups to platform modules (sensor.py, binary_sensor.py)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update callback dynamically."""
    _LOGGER.debug("Options updated for entry %s, updating coordinator settings", entry.entry_id)
    coordinator: AnkerSolixBluetoothUpdateCoordinator | None = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator:
        await coordinator.async_update_options_handler()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry, cleanly stopping coordinator connection clients."""
    _LOGGER.debug("Unloading Anker Solix F2000 entry ID: %s", entry.entry_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: AnkerSolixBluetoothUpdateCoordinator | None = (
            hass.data[DOMAIN].pop(entry.entry_id, None)
        )
        if coordinator:
            # Tear down persistent Bleak connections and timers cleanly
            await coordinator.async_stop()

    return unload_ok
