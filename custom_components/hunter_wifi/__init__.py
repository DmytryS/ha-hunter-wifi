"""Hunter WiFi integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_PROGRAMS,
    CONF_ZONES,
    DEFAULT_DEVICE_NAME,
    DEFAULT_ZONE_DURATION_MINUTES,
    DOMAIN,
)

PLATFORMS = ["button", "number"]


def _normalize_int_list(raw_values: Iterable[int] | None) -> list[int]:
    """Normalize incoming config list of ids to sorted unique ints."""
    if raw_values is None:
        return []
    return sorted({int(value) for value in raw_values})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hunter WiFi from config entry."""
    device_name = entry.options.get(
        CONF_DEVICE_NAME,
        entry.data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
    )
    host = entry.options.get(CONF_HOST, entry.data[CONF_HOST])
    zones = _normalize_int_list(
        entry.options.get(CONF_ZONES, entry.data.get(CONF_ZONES, []))
    )
    programs = _normalize_int_list(
        entry.options.get(CONF_PROGRAMS, entry.data.get(CONF_PROGRAMS, []))
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        CONF_DEVICE_NAME: device_name,
        CONF_HOST: host,
        CONF_ZONES: zones,
        CONF_PROGRAMS: programs,
        "zone_durations": dict.fromkeys(zones, DEFAULT_ZONE_DURATION_MINUTES),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Hunter WiFi config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
