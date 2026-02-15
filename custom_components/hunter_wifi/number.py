"""Number entities for Hunter WiFi."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import RestoreNumber
from homeassistant.const import UnitOfTime
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

from .const import (
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_ZONES,
    DEFAULT_ZONE_DURATION_MINUTES,
    DOMAIN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up per-zone watering duration entities."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    device_name: str = entry_data[CONF_DEVICE_NAME]
    host: str = entry_data[CONF_HOST]
    zones: list[int] = entry_data[CONF_ZONES]
    slug = slugify(device_name)
    async_add_entities(
        [
            HunterZoneDurationNumber(hass, entry, device_name, slug, host, zone)
            for zone in zones
        ]
    )


class HunterZoneDurationNumber(RestoreNumber):
    """Editable zone duration used for /start/zone time parameter."""

    _attr_has_entity_name = True
    _attr_mode = "box"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_native_min_value = 1
    _attr_native_max_value = 240
    _attr_native_step = 1
    _attr_icon = "mdi:timer-outline"

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device_name: str,
        slug: str,
        host: str,
        zone: int,
    ) -> None:
        """Initialize zone duration entity."""
        self.hass = hass
        self.config_entry = config_entry
        self._device_name = device_name
        self._slug = slug
        self._host = host
        self._zone = zone
        self._attr_name = f"Zone {zone} Duration"
        self._attr_unique_id = f"zone_{zone}_duration_{config_entry.entry_id}"
        self._attr_suggested_object_id = f"{self._slug}_zone_{zone}_duration"
        self._attr_native_value = float(DEFAULT_ZONE_DURATION_MINUTES)

    async def async_added_to_hass(self) -> None:
        """Restore previous value if available."""
        await super().async_added_to_hass()
        if (last_number_data := await self.async_get_last_number_data()) is not None:
            self._attr_native_value = last_number_data.native_value

        self._update_runtime_duration()

    async def async_set_native_value(self, value: float) -> None:
        """Set zone watering duration in minutes."""
        self._attr_native_value = value
        self._update_runtime_duration()
        self.async_write_ha_state()

    def _update_runtime_duration(self) -> None:
        """Sync the runtime zone duration map used by start buttons."""
        entry_data = self.hass.data[DOMAIN][self.config_entry.entry_id]
        zone_durations: dict[int, int] = entry_data["zone_durations"]
        zone_durations[self._zone] = int(
            self.native_value or DEFAULT_ZONE_DURATION_MINUTES
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return parent device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=self._device_name,
            manufacturer="Hunter",
            model="WiFi Controller",
            configuration_url=f"http://{self._host}",
        )
