"""Worx Vision integration."""

from __future__ import annotations

import logging
from functools import partial
from pathlib import Path
from typing import Any

import voluptuous as vol
from pyworxcloud import WorxCloud

from homeassistant.components.frontend import add_extra_js_url, remove_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.setup import async_when_setup_or_start

from .const import (
    ATTR_BOUNDARY,
    ATTR_ENABLED,
    ATTR_ENTRIES,
    ATTR_RUNTIME,
    ATTR_TIME_EXTENSION,
    ATTR_ZONE,
    CONF_CLOUD,
    CONF_SERIAL_NUMBER,
    DATA_FRONTEND_CARD_REGISTERED,
    DEFAULT_CLOUD,
    DOMAIN,
    FRONTEND_CARD_MODULE_URL,
    FRONTEND_CARD_URL_PATH,
    PLATFORMS,
    SERVICE_OTS,
    SERVICE_SET_SCHEDULE,
    SERVICE_START_ZONE,
)
from .coordinator import WorxVisionCoordinator

_LOGGER = logging.getLogger(__name__)

START_ZONE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SERIAL_NUMBER): cv.string,
        vol.Required(ATTR_ZONE): vol.Coerce(int),
    }
)

SET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SERIAL_NUMBER): cv.string,
        vol.Optional(ATTR_ENABLED): cv.boolean,
        vol.Optional(ATTR_ENTRIES): [dict],
        vol.Optional(ATTR_TIME_EXTENSION): vol.Coerce(int),
    }
)

OTS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SERIAL_NUMBER): cv.string,
        vol.Optional(ATTR_BOUNDARY, default=False): cv.boolean,
        vol.Required(ATTR_RUNTIME): vol.Coerce(int),
    }
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration from YAML (not used)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Worx Vision from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    await _async_setup_frontend_card(hass)

    cloud = WorxCloud(
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
        cloud=entry.data.get(CONF_CLOUD, DEFAULT_CLOUD),
    )
    coordinator = WorxVisionCoordinator(
        hass,
        cloud,
        serial_number=entry.data.get(CONF_SERIAL_NUMBER),
    )

    try:
        await coordinator.async_setup()
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await coordinator.async_shutdown()
        raise

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_START_ZONE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_START_ZONE,
            partial(_handle_start_zone, hass),
            schema=START_ZONE_SCHEMA,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_SCHEDULE,
            partial(_handle_set_schedule, hass),
            schema=SET_SCHEDULE_SCHEMA,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_OTS,
            partial(_handle_ots, hass),
            schema=OTS_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    coordinator: WorxVisionCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.async_shutdown()

    if not hass.data[DOMAIN]:
        for service in (SERVICE_START_ZONE, SERVICE_SET_SCHEDULE, SERVICE_OTS):
            if hass.services.has_service(DOMAIN, service):
                hass.services.async_remove(DOMAIN, service)
        if hass.data.pop(DATA_FRONTEND_CARD_REGISTERED, False):
            remove_extra_js_url(hass, FRONTEND_CARD_MODULE_URL)

    return unload_ok


async def _async_setup_frontend_card(hass: HomeAssistant) -> None:
    """Register and load the frontend card resource once."""
    if hass.data.get(DATA_FRONTEND_CARD_REGISTERED):
        return

    card_dir = Path(__file__).parent / "www"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_CARD_URL_PATH, str(card_dir), cache_headers=False)]
    )

    @callback
    def _register_frontend_resource(*_: Any) -> None:
        add_extra_js_url(hass, FRONTEND_CARD_MODULE_URL)

    async_when_setup_or_start(hass, "frontend", _register_frontend_resource)
    hass.data[DATA_FRONTEND_CARD_REGISTERED] = True


def _iter_coordinators(
    hass: HomeAssistant,
    serial_number: str | None,
) -> list[WorxVisionCoordinator]:
    """Return matching coordinators for optional serial filter."""
    coordinators = list(hass.data.get(DOMAIN, {}).values())
    if serial_number is None:
        return coordinators

    return [
        coordinator
        for coordinator in coordinators
        if coordinator.serial_number == serial_number
    ]


async def _handle_start_zone(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle start zone service."""
    serial_number = call.data.get(CONF_SERIAL_NUMBER)
    zone = call.data[ATTR_ZONE]

    targets = _iter_coordinators(hass, serial_number)
    if not targets:
        raise HomeAssistantError("No matching mower found")

    for coordinator in targets:
        await coordinator.async_start_zone(zone)


async def _handle_set_schedule(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle set schedule service."""
    serial_number = call.data.get(CONF_SERIAL_NUMBER)

    targets = _iter_coordinators(hass, serial_number)
    if not targets:
        raise HomeAssistantError("No matching mower found")

    enabled = call.data.get(ATTR_ENABLED)
    entries = call.data.get(ATTR_ENTRIES)
    time_extension = call.data.get(ATTR_TIME_EXTENSION)

    for coordinator in targets:
        await coordinator.async_set_schedule(enabled, entries, time_extension)


async def _handle_ots(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle one-time-schedule service."""
    serial_number = call.data.get(CONF_SERIAL_NUMBER)

    targets = _iter_coordinators(hass, serial_number)
    if not targets:
        raise HomeAssistantError("No matching mower found")

    boundary = call.data[ATTR_BOUNDARY]
    runtime = call.data[ATTR_RUNTIME]

    for coordinator in targets:
        await coordinator.async_ots(boundary, runtime)
