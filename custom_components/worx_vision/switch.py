"""Switches for Worx Vision."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WorxVisionCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worx Vision switches."""
    coordinator: WorxVisionCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WorxVisionScheduleSwitch(coordinator)])


class WorxVisionScheduleSwitch(
    CoordinatorEntity[WorxVisionCoordinator],
    SwitchEntity,
):
    """Enable or disable mower schedule."""

    _attr_has_entity_name = True
    _attr_translation_key = "schedule"

    def __init__(self, coordinator: WorxVisionCoordinator) -> None:
        """Initialize switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.serial_number}_schedule"

    @property
    def is_on(self) -> bool:
        """Return switch state."""
        return bool(self.coordinator.data.schedule_enabled)

    @property
    def available(self) -> bool:
        """Return availability state."""
        return super().available and self.coordinator.data.online

    async def async_turn_on(self, **kwargs) -> None:
        """Turn schedule on."""
        await self.coordinator.async_toggle_schedule(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn schedule off."""
        await self.coordinator.async_toggle_schedule(False)
