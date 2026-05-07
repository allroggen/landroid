"""Binary sensors for Worx Vision."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WorxVisionCoordinator


BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="is_mowing",
        translation_key="is_mowing",
        icon="mdi:robot-mower-outline",
    ),
    BinarySensorEntityDescription(
        key="rain_delay_active",
        translation_key="rain_delay_active",
        icon="mdi:weather-rainy",
    ),
    BinarySensorEntityDescription(
        key="error",
        translation_key="error",
        icon="mdi:alert-circle",
    ),
    BinarySensorEntityDescription(
        key="charging",
        translation_key="charging",
        icon="mdi:battery-charging",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worx Vision binary sensors."""
    coordinator: WorxVisionCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        WorxVisionBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSORS
    )


class WorxVisionBinarySensorEntity(
    CoordinatorEntity[WorxVisionCoordinator],
    BinarySensorEntity,
):
    """Worx Vision binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WorxVisionCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.serial_number}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return binary state."""
        data = self.coordinator.data
        key = self.entity_description.key

        if key == "is_mowing":
            return data.is_mowing
        if key == "rain_delay_active":
            return data.rain_delay_active
        if key == "error":
            return data.error_id not in (None, 0)
        if key == "charging":
            return bool(data.charging)

        return False

    @property
    def available(self) -> bool:
        """Return availability state."""
        return super().available and self.coordinator.data.online

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes for error sensor."""
        if self.entity_description.key != "error":
            return {}

        return {
            "error_id": self.coordinator.data.error_id,
            "error": self.coordinator.data.error_description,
        }
