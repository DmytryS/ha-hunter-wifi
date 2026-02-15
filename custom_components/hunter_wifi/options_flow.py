"""Options flow for Hunter WiFi."""

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
    MAX_PROGRAM,
    MAX_ZONE,
)

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


def _build_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Build options flow schema."""
    schema: dict[vol.Marker, object] = {
        vol.Required(
            CONF_DEVICE_NAME,
            default=defaults.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
        ): str,
        vol.Required(CONF_HOST, default=defaults[CONF_HOST]): str,
    }
    for zone in range(1, MAX_ZONE + 1):
        schema[
            vol.Optional(f"zone_{zone}", default=defaults.get(f"zone_{zone}", False))
        ] = bool
    for program in range(1, MAX_PROGRAM + 1):
        schema[
            vol.Optional(
                f"program_{program}", default=defaults.get(f"program_{program}", False)
            )
        ] = bool
    return vol.Schema(schema)


class HunterWifiOptionsFlow(config_entries.OptionsFlow):
    """Handle Hunter WiFi options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        errors: dict[str, str] = {}
        defaults = _defaults_from_entry(self.config_entry)

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
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_DEVICE_NAME: device_name,
                        CONF_HOST: host,
                        CONF_ZONES: zones,
                        CONF_PROGRAMS: programs,
                    },
                )
            defaults = user_input

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(defaults),
            errors=errors,
        )


def _defaults_from_entry(config_entry: config_entries.ConfigEntry) -> dict[str, Any]:
    """Build checkbox defaults from config entry."""
    device_name = config_entry.options.get(
        CONF_DEVICE_NAME,
        config_entry.data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
    )
    host = config_entry.options.get(CONF_HOST, config_entry.data[CONF_HOST])
    zones = config_entry.options.get(CONF_ZONES, config_entry.data.get(CONF_ZONES, []))
    programs = config_entry.options.get(
        CONF_PROGRAMS, config_entry.data.get(CONF_PROGRAMS, [])
    )
    defaults: dict[str, Any] = {CONF_DEVICE_NAME: device_name, CONF_HOST: host}
    for zone in range(1, MAX_ZONE + 1):
        defaults[f"zone_{zone}"] = zone in zones
    for program in range(1, MAX_PROGRAM + 1):
        defaults[f"program_{program}"] = program in programs
    return defaults
