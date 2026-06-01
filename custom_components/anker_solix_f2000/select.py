"""Select platform for Anker Solix F2000 Bluetooth integration.

This module exposes select dropdown entities for LED light, display settings, and end timers.
"""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AnkerSolixBluetoothUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


# Helper functions to convert between shutdown timer seconds and dropdown string options
def seconds_to_option(seconds: int) -> str:
    """Convert duration in seconds to a human-readable dropdown option string."""
    if seconds <= 0:
        return "Disabled"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    rem_mins = minutes % 60
    if rem_mins == 0:
        return f"{hours}h"
    return f"{hours}h {rem_mins}m"


def option_to_seconds(option: str) -> int:
    """Convert human-readable dropdown option string to duration in seconds."""
    if option == "Disabled":
        return 0
    if "h" in option:
        parts = option.split("h")
        hours = int(parts[0].strip())
        minutes = 0
        if len(parts) > 1 and "m" in parts[1]:
            minutes = int(parts[1].replace("m", "").strip())
        return (hours * 60 + minutes) * 60
    if "m" in option:
        minutes = int(option.replace("m", "").strip())
        return minutes * 60
    return 0


# Pre-generate shutdown timer option list (5-minute intervals up to 18 hours)
TIMER_OPTIONS: list[str] = ["Disabled"]
for minutes_count in range(5, 1085, 5):
    TIMER_OPTIONS.append(seconds_to_option(minutes_count * 60))

# Mappings for Screen Timeout (20s, 30s, 1m, 5m, 30m)
TIMEOUT_MAP = {
    "20s": 20,
    "30s": 30,
    "1m": 60,
    "5m": 300,
    "30m": 1800,
}
REVERSE_TIMEOUT_MAP = {v: k for k, v in TIMEOUT_MAP.items()}

# Mappings for Screen Brightness (Low, Mid, High, Max)
BRIGHTNESS_OPTIONS = ["Low", "Mid", "High", "Max"]

# Mappings for LED light (Off, Low, Mid, High, SOS)
LED_OPTIONS = ["OFF", "LOW", "MID", "HIGH", "SOS"]


SELECT_DESCRIPTIONS: list[SelectEntityDescription] = [
    SelectEntityDescription(
        key="led_state",
        name="LED Light Brightness",
        options=LED_OPTIONS,
        icon="mdi:led-on",
    ),
    SelectEntityDescription(
        key="screen_brightness",
        name="Screen Brightness",
        options=BRIGHTNESS_OPTIONS,
        icon="mdi:brightness-6",
    ),
    SelectEntityDescription(
        key="screen_timeout",
        name="Screen Timeout",
        options=list(TIMEOUT_MAP.keys()),
        icon="mdi:progress-clock",
    ),
    SelectEntityDescription(
        key="ac_outlet_timer",
        name="AC Sockets Shutdown Timer",
        options=TIMER_OPTIONS,
        icon="mdi:timer-outline",
    ),
    SelectEntityDescription(
        key="dc_12v_port1_timer",
        name="12V Car Port Shutdown Timer",
        options=TIMER_OPTIONS,
        icon="mdi:timer-outline",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Anker Solix F2000 select entities from ConfigEntry."""
    coordinator: AnkerSolixBluetoothUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    selects = [
        AnkerSolixSelect(coordinator, desc)
        for desc in SELECT_DESCRIPTIONS
    ]
    async_add_entities(selects)


class AnkerSolixSelect(
    CoordinatorEntity[AnkerSolixBluetoothUpdateCoordinator],
    SelectEntity,
):
    """Representation of an Anker Solix select dropdown control."""

    def __init__(
        self,
        coordinator: AnkerSolixBluetoothUpdateCoordinator,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
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
    def current_option(self) -> str | None:
        """Return the current active dropdown option option."""
        if self.coordinator.data is None:
            return None

        val = self.coordinator.data.get(self.entity_description.key)
        if val is None:
            return None

        key = self.entity_description.key

        if key == "led_state":
            led_str = str(val).upper()
            return led_str if led_str in LED_OPTIONS else "OFF"

        if key == "screen_brightness":
            try:
                brightness_idx = int(val)
                if 0 <= brightness_idx < len(BRIGHTNESS_OPTIONS):
                    return BRIGHTNESS_OPTIONS[brightness_idx]
            except (ValueError, TypeError):
                pass
            return "Mid"

        if key == "screen_timeout":
            try:
                timeout_s = int(val)
                if timeout_s in REVERSE_TIMEOUT_MAP:
                    return REVERSE_TIMEOUT_MAP[timeout_s]
            except (ValueError, TypeError):
                pass
            return "30s"

        if key in ("ac_outlet_timer", "dc_12v_port1_timer"):
            try:
                seconds = int(val)
                # Round to the nearest 5-minute interval for alignment
                minutes = round(seconds / 300) * 5
                rounded_seconds = minutes * 60
                opt = seconds_to_option(rounded_seconds)
                if opt in self.entity_description.options:
                    return opt
            except (ValueError, TypeError):
                pass
            return "Disabled"

        return None

    async def async_select_option(self, option: str) -> None:
        """Set the F2000 control state to the chosen option."""
        if option not in self.entity_description.options:
            _LOGGER.warning("Invalid select option: %s", option)
            return

        key = self.entity_description.key

        if key == "led_state":
            cmd_id = 0x8B
            payload = bytes([LED_OPTIONS.index(option)])
            await self.coordinator.async_send_control_command(cmd_id, payload)

        elif key == "screen_brightness":
            cmd_id = 0x88
            payload = bytes([BRIGHTNESS_OPTIONS.index(option)])
            await self.coordinator.async_send_control_command(cmd_id, payload)

        elif key == "screen_timeout":
            cmd_id = 0x82
            seconds = TIMEOUT_MAP[option]
            payload = seconds.to_bytes(2, byteorder="little")
            await self.coordinator.async_send_control_command(cmd_id, payload)

        elif key == "ac_outlet_timer":
            if option == self.current_option:
                _LOGGER.debug(
                    "AC Sockets Shutdown Timer already set to %s, ignoring redundant update",
                    option,
                )
                return
            cmd_id = 0x02
            seconds = option_to_seconds(option)
            payload = seconds.to_bytes(2, byteorder="little")
            await self.coordinator.async_send_control_command(cmd_id, payload)

        elif key == "dc_12v_port1_timer":
            if option == self.current_option:
                _LOGGER.debug(
                    "12V Car Port Shutdown Timer already set to %s, ignoring redundant update",
                    option,
                )
                return
            cmd_id = 0x03
            seconds = option_to_seconds(option)
            payload = seconds.to_bytes(2, byteorder="little")
            await self.coordinator.async_send_control_command(cmd_id, payload)
