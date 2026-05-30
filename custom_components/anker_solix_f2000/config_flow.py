"""Config flow for Anker Solix F2000 Bluetooth integration.

This module implements user configuration flows, enabling plug-and-play auto-discovery of
nearby F2000 power stations, BLE advertisement name filtering, and a manual entry fallback
for custom environments.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import bluetooth
from homeassistant.const import CONF_ADDRESS, CONF_NAME

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AnkerSolixF2000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Anker Solix F2000."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step of config flow (auto-discovery selection)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_address = user_input[CONF_ADDRESS]

            # Direct user to manual fallback step if requested
            if selected_address == "manual":
                return await self.async_step_manual()

            # Retrieve resolved name and save ConfigEntry
            name = self._discovered_devices[selected_address]
            await self.async_set_unique_id(selected_address)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=name,
                data={CONF_ADDRESS: selected_address, CONF_NAME: name},
            )

        # Retrieve discovered BLE devices using HA's central Bluetooth scanner
        discovered = bluetooth.async_discovered_service_info(self.hass)
        device_options: dict[str, str] = {}

        for info in discovered:
            name = info.name or ""
            if any(term in name for term in ["767", "PowerHouse", "F2000", "Anker"]):
                self._discovered_devices[info.address] = name
                device_options[info.address] = f"{name} ({info.address})"

        # Insert manual option
        device_options["manual"] = "Manually Enter MAC Address..."

        # Show selection form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): vol.In(device_options)
            }),
            errors=errors,
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle manual entry of MAC address and device name."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip().upper()
            name = user_input[CONF_NAME].strip() or "767_PowerHouse"

            # Standard MAC format verification
            if len(address.split(":")) != 6:
                errors[CONF_ADDRESS] = "invalid_mac"
            else:
                await self.async_set_unique_id(address)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={CONF_ADDRESS: address, CONF_NAME: name},
                )

        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): str,
                vol.Optional(CONF_NAME, default="767_PowerHouse"): str,
            }),
            errors=errors,
        )
