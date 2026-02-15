"""Config flow for Hunter WiFi."""

from __future__ import annotations

import ipaddress
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_PROGRAMS,
    CONF_ZONES,
    DEFAULT_DEVICE_NAME,
    DOMAIN,
    MAX_PROGRAM,
    MAX_ZONE,
)
from .options_flow import HunterWifiOptionsFlow

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult


def _selected_from_input(
    user_input: dict[str, Any], prefix: str, max_value: int
) -> list[int]:
    """Convert checkbox values to list of selected numeric ids."""
    return [
        value
        for value in range(1, max_value + 1)
        if user_input.get(f"{prefix}_{value}", False)
    ]


def _build_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build config flow schema."""
    data = defaults or {}
    schema: dict[vol.Marker, object] = {
        vol.Required(
            CONF_DEVICE_NAME,
            default=data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
        ): str,
        vol.Required(CONF_HOST, default=data.get(CONF_HOST, "")): str,
    }
    for zone in range(1, MAX_ZONE + 1):
        schema[vol.Optional(f"zone_{zone}", default=data.get(f"zone_{zone}", True))] = (
            bool
        )
    for program in range(1, MAX_PROGRAM + 1):
        schema[
            vol.Optional(
                f"program_{program}", default=data.get(f"program_{program}", True)
            )
        ] = bool
    return vol.Schema(schema)


class HunterWifiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hunter WiFi config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HunterWifiOptionsFlow:
        """Get options flow."""
        return HunterWifiOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle initial config step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            device_name = user_input[CONF_DEVICE_NAME].strip()
            host = user_input[CONF_HOST].strip()
            try:
                ipaddress.ip_address(host)
            except ValueError:
                errors[CONF_HOST] = "invalid_ip"
            if not device_name:
                errors[CONF_DEVICE_NAME] = "required"

            zones = _selected_from_input(user_input, "zone", MAX_ZONE)
            programs = _selected_from_input(user_input, "program", MAX_PROGRAM)

            if not zones and not programs:
                errors["base"] = "select_at_least_one"

            if not errors:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=device_name,
                    data={
                        CONF_DEVICE_NAME: device_name,
                        CONF_HOST: host,
                        CONF_ZONES: zones,
                        CONF_PROGRAMS: programs,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input),
            errors=errors,
        )
