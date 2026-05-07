"""Data coordinator for Worx Vision."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

from pyworxcloud import (
    LandroidEvent,
    ScheduleEntry,
    ScheduleModel,
    WorxCloud,
)
from pyworxcloud.exceptions import MowerNotFoundError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class WorxVisionData:
    """Normalized mower data for Home Assistant entities."""

    serial_number: str
    name: str
    model: str | None
    online: bool
    battery_percent: int | None
    charging: bool | None
    status_id: int | None
    status_description: str | None
    error_id: int | None
    error_description: str | None
    is_mowing: bool
    is_docked: bool
    is_paused: bool
    rain_delay_active: bool
    schedule_enabled: bool | None
    total_mowing_time_minutes: int | None
    last_update: datetime | None
    latitude: float | None
    longitude: float | None


class WorxVisionCoordinator(DataUpdateCoordinator[WorxVisionData]):
    """Coordinate updates from pyworxcloud."""

    def __init__(
        self,
        hass: HomeAssistant,
        cloud: WorxCloud,
        serial_number: str | None = None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Worx Vision",
            update_interval=UPDATE_INTERVAL,
        )
        self.cloud = cloud
        self.serial_number = serial_number
        self.device_name: str | None = None

    async def async_setup(self) -> None:
        """Authenticate, connect and resolve target mower."""
        await self.cloud.authenticate()
        await self.cloud.connect()

        if self.serial_number is None:
            if not self.cloud.devices:
                raise UpdateFailed("No mower found for account")
            first = next(iter(self.cloud.devices.values()))
            self.serial_number = str(getattr(first, "serial_number"))

        device = self._find_device()
        self.device_name = str(getattr(device, "name", self.serial_number))

        def _event_callback(**kwargs: Any) -> None:
            name = kwargs.get("name")
            if name and self.device_name and name != self.device_name:
                return
            self.hass.loop.call_soon_threadsafe(self.async_set_updated_data, self._extract())

        self.cloud.set_callback(LandroidEvent.DATA_RECEIVED, _event_callback)
        self.cloud.set_callback(LandroidEvent.API, _event_callback)

    async def async_shutdown(self) -> None:
        """Disconnect cloud API and MQTT."""
        await self.cloud.disconnect()

    def _find_device(self) -> Any:
        """Return device for selected serial number."""
        for device in self.cloud.devices.values():
            if str(getattr(device, "serial_number", "")) == self.serial_number:
                return device

        raise MowerNotFoundError(f"Mower with serial number '{self.serial_number}' not found")

    def _extract(self) -> WorxVisionData:
        """Build normalized data object from pyworxcloud device model."""
        device = self._find_device()

        battery = getattr(device, "battery", {})
        status = getattr(device, "status", {})
        error = getattr(device, "error", {})
        rain = getattr(device, "rainsensor", {})
        schedules = getattr(device, "schedules", {})

        status_id = _safe_int(status.get("id"))
        status_description = _safe_str(status.get("description"))
        error_id = _safe_int(error.get("id"))
        error_description = _safe_str(error.get("description"))

        mowing = status_id in {7, 8, 32}
        docked = status_id in {1, 5, 30, 104}
        paused = status_id == 34

        gps = getattr(device, "gps", {})
        latitude = _safe_float(gps.get("latitude")) if isinstance(gps, dict) else None
        longitude = _safe_float(gps.get("longitude")) if isinstance(gps, dict) else None

        stats = getattr(device, "statistics", {})
        total_minutes = None
        if isinstance(stats, dict):
            total_minutes = _safe_int(stats.get("worktime"))

        return WorxVisionData(
            serial_number=str(getattr(device, "serial_number", self.serial_number)),
            name=str(getattr(device, "name", self.serial_number)),
            model=_safe_str(getattr(device, "model", None)),
            online=bool(getattr(device, "online", False)),
            battery_percent=_safe_int(battery.get("percent") if isinstance(battery, dict) else None),
            charging=_safe_bool(battery.get("charging") if isinstance(battery, dict) else None),
            status_id=status_id,
            status_description=status_description,
            error_id=error_id,
            error_description=error_description,
            is_mowing=mowing,
            is_docked=docked,
            is_paused=paused,
            rain_delay_active=bool(getattr(device, "raindelay_active", rain.get("triggered", False))),
            schedule_enabled=_safe_bool(schedules.get("active") if isinstance(schedules, dict) else None),
            total_mowing_time_minutes=total_minutes,
            last_update=getattr(device, "updated", None),
            latitude=latitude,
            longitude=longitude,
        )

    async def _async_update_data(self) -> WorxVisionData:
        """Fetch latest state from cloud."""
        try:
            await self.cloud.update(self.serial_number)
            return self._extract()
        except Exception as err:
            raise UpdateFailed(f"Failed to update mower data: {err}") from err

    async def async_start(self) -> None:
        """Start mowing."""
        await self.cloud.start(self.serial_number)
        await self.async_request_refresh()

    async def async_pause(self) -> None:
        """Pause mowing."""
        await self.cloud.pause(self.serial_number)
        await self.async_request_refresh()

    async def async_dock(self) -> None:
        """Return mower to dock."""
        await self.cloud.home(self.serial_number)
        await self.async_request_refresh()

    async def async_toggle_schedule(self, enabled: bool) -> None:
        """Enable or disable schedule."""
        await self.cloud.toggle_schedule(self.serial_number, enabled)
        await self.async_request_refresh()

    async def async_start_zone(self, zone: int) -> None:
        """Start mowing from zone."""
        await self.cloud.setzone(self.serial_number, zone)
        await self.async_request_refresh()

    async def async_ots(self, boundary: bool, runtime: int) -> None:
        """Start one-time schedule run."""
        await self.cloud.ots(self.serial_number, boundary, runtime)
        await self.async_request_refresh()

    async def async_set_schedule(
        self,
        enabled: bool | None,
        entries: list[dict[str, Any]] | None,
        time_extension: int | None,
    ) -> None:
        """Set schedule model from service input."""
        current = self.cloud.get_schedule(self.serial_number)
        new_entries = current.entries

        if entries is not None:
            new_entries = [
                ScheduleEntry(
                    entry_id=str(item.get("id", f"service_{uuid4()}")),
                    day=str(item["day"]),
                    start=str(item["start"]),
                    duration=int(item["duration"]),
                    boundary=(
                        bool(item["boundary"])
                        if item.get("boundary") is not None
                        else None
                    ),
                    source=str(item.get("source", "service")),
                    secondary=bool(item.get("secondary", False)),
                )
                for item in entries
            ]

        model = ScheduleModel(
            enabled=current.enabled if enabled is None else bool(enabled),
            time_extension=(
                current.time_extension if time_extension is None else int(time_extension)
            ),
            entries=new_entries,
            protocol=current.protocol,
        )

        await self.cloud.set_schedule(self.serial_number, model)
        await self.async_request_refresh()


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None
