"""Lawn mower platform for Worx Vision."""

from __future__ import annotations

from typing import Any

from homeassistant.components import lawn_mower as lawn_mower_platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WorxVisionCoordinator

LawnMowerEntity = lawn_mower_platform.LawnMowerEntity
LawnMowerActivity = lawn_mower_platform.LawnMowerActivity
LawnMowerEntityFeature = getattr(lawn_mower_platform, "LawnMowerEntityFeature", None)

FEATURE_START = int(getattr(LawnMowerEntityFeature, "START_MOWING", 0))
FEATURE_PAUSE = int(getattr(LawnMowerEntityFeature, "PAUSE", 0))
FEATURE_DOCK = int(getattr(LawnMowerEntityFeature, "DOCK", 0))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worx Vision lawn mower entity."""
    coordinator: WorxVisionCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WorxVisionLawnMowerEntity(coordinator)])


class WorxVisionLawnMowerEntity(
    CoordinatorEntity[WorxVisionCoordinator],
    LawnMowerEntity,
):
    """Representation of a Worx Vision mower."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: WorxVisionCoordinator) -> None:
        """Initialize the mower entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.serial_number}_mower"
        self._attr_name = coordinator.data.name
        self._attr_supported_features = FEATURE_START | FEATURE_PAUSE | FEATURE_DOCK

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return super().available and self.coordinator.data.online

    @property
    def activity(self) -> Any:
        """Return mower activity state."""
        data = self.coordinator.data

        if data.error_id not in (None, 0):
            return getattr(LawnMowerActivity, "ERROR", None)
        if data.is_mowing:
            return getattr(LawnMowerActivity, "MOWING", None)
        if data.is_paused:
            return getattr(LawnMowerActivity, "PAUSED", None)
        if data.is_docked:
            return getattr(LawnMowerActivity, "DOCKED", None)
        return getattr(LawnMowerActivity, "IDLE", None)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        data = self.coordinator.data
        return {
            "serial_number": data.serial_number,
            "model": data.model,
            "status_id": data.status_id,
            "status": data.status_description,
            "error_id": data.error_id,
            "error": data.error_description,
            "charging": data.charging,
            "rain_delay_active": data.rain_delay_active,
        }

    async def async_start_mowing(self) -> None:
        """Start mowing."""
        await self.coordinator.async_start()

    async def async_pause(self) -> None:
        """Pause mowing."""
        await self.coordinator.async_pause()

    async def async_dock(self) -> None:
        """Dock mower."""
        await self.coordinator.async_dock()
