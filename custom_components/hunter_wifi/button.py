"""Button entities for Hunter WiFi."""

from __future__ import annotations

import logging
from asyncio import timeout
from typing import TYPE_CHECKING

import aiohttp
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

from .const import CONF_DEVICE_NAME, CONF_HOST, CONF_PROGRAMS, CONF_ZONES, DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Hunter buttons for configured zones and programs."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    device_name: str = entry_data[CONF_DEVICE_NAME]
    host: str = entry_data[CONF_HOST]
    zones: list[int] = entry_data[CONF_ZONES]
    programs: list[int] = entry_data[CONF_PROGRAMS]
    slug = slugify(device_name)

    entities: list[HunterActionButton] = []
    for zone in zones:
        entities.append(
            HunterActionButton(
                hass,
                entry,
                device_name,
                slug,
                host,
                "start_zone",
                zone=zone,
            )
        )
        entities.append(
            HunterActionButton(
                hass,
                entry,
                device_name,
                slug,
                host,
                "stop_zone",
                zone=zone,
            )
        )
    entities.extend(
        [
            HunterActionButton(
                hass,
                entry,
                device_name,
                slug,
                host,
                "start_program",
                program=program,
            )
            for program in programs
        ]
    )
    entities.append(
        HunterActionButton(
            hass,
            entry,
            device_name,
            slug,
            host,
            "stop_all_zones",
            zones=zones,
        )
    )

    async_add_entities(entities)


class HunterActionButton(ButtonEntity):
    """Stateless action button for Hunter API."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device_name: str,
        slug: str,
        host: str,
        action: str,
        zone: int | None = None,
        program: int | None = None,
        zones: list[int] | None = None,
    ) -> None:
        """Initialize Hunter action button."""
        self.hass = hass
        self.config_entry = config_entry
        self._device_name = device_name
        self._slug = slug
        self._host = host
        self._action = action
        self._zone = zone
        self._program = program
        self._zones = zones or []

        if action == "stop_all_zones":
            self._attr_unique_id = f"{action}_{config_entry.entry_id}"
            self._attr_name = "Stop All Zones"
            self._attr_suggested_object_id = f"{self._slug}_{action}"
        elif zone is not None:
            self._attr_unique_id = f"{action}_{zone}_{config_entry.entry_id}"
            action_label = "Start" if action == "start_zone" else "Stop"
            self._attr_name = f"{action_label} Zone {zone}"
            self._attr_suggested_object_id = f"{self._slug}_{action}_{zone}"
        else:
            self._attr_unique_id = f"{action}_{program}_{config_entry.entry_id}"
            self._attr_name = f"Start Program {program}"
            self._attr_suggested_object_id = f"{self._slug}_{action}_{program}"

        if action.startswith("start"):
            self._attr_icon = "mdi:play-circle-outline"
        else:
            self._attr_icon = "mdi:stop-circle-outline"

    async def async_press(self) -> None:
        """Trigger start/stop action via Hunter HTTP API."""
        session = async_get_clientsession(self.hass)
        if self._action == "stop_all_zones":
            await self._async_stop_all_zones(session)
            return

        url = "unknown"
        try:
            url = self._build_url()
            async with timeout(10):
                async with session.get(url) as response:
                    response.raise_for_status()
        except (aiohttp.ClientError, TimeoutError, ValueError):
            LOGGER.exception("Failed Hunter request for %s", url)

    async def _async_stop_all_zones(self, session: aiohttp.ClientSession) -> None:
        """Stop all configured zones one by one."""
        for zone in self._zones:
            url = f"http://{self._host}/api/stop/zone/{zone}"
            try:
                async with timeout(10):
                    async with session.get(url) as response:
                        response.raise_for_status()
            except (aiohttp.ClientError, TimeoutError):
                LOGGER.exception("Failed Hunter request for %s", url)

    def _build_url(self) -> str:
        """Build API URL for current action."""
        if self._zone is not None:
            if self._action == "start_zone":
                entry_data = self.hass.data[DOMAIN][self.config_entry.entry_id]
                zone_durations: dict[int, int] = entry_data["zone_durations"]
                duration = int(zone_durations.get(self._zone, 5))
                return (
                    f"http://{self._host}/api/start/zone/{self._zone}?time={duration}"
                )
            return f"http://{self._host}/api/stop/zone/{self._zone}"

        if self._action == "start_program":
            return f"http://{self._host}/api/start/program/{self._program}"
        msg = f"Unsupported action requested: {self._action}"
        raise ValueError(msg)

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
