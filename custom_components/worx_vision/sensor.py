"""Sensor platform for Worx Vision."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WorxVisionCoordinator


SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery",
        translation_key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="error_code",
        translation_key="error_code",
        icon="mdi:alert-circle-outline",
    ),
    SensorEntityDescription(
        key="error_message",
        translation_key="error_message",
        icon="mdi:alert-octagon-outline",
    ),
    SensorEntityDescription(
        key="total_mowing_time",
        translation_key="total_mowing_time",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:timer-outline",
    ),
    SensorEntityDescription(
        key="last_update",
        translation_key="last_update",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-outline",
    ),
    SensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:robot-mower-outline",
    ),
    SensorEntityDescription(
        key="latitude",
        translation_key="latitude",
        icon="mdi:latitude",
    ),
    SensorEntityDescription(
        key="longitude",
        translation_key="longitude",
        icon="mdi:longitude",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Worx Vision sensor entities."""
    coordinator: WorxVisionCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        WorxVisionSensorEntity(coordinator, description) for description in SENSORS
    )


class WorxVisionSensorEntity(
    CoordinatorEntity[WorxVisionCoordinator],
    SensorEntity,
):
    """Worx Vision sensor entity."""

    _attr_has_entity_name = True
    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: WorxVisionCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.serial_number}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return sensor value."""
        data = self.coordinator.data
        key = self.entity_description.key

        values = {
            "battery": data.battery_percent,
            "error_code": data.error_id,
            "error_message": data.error_description,
            "total_mowing_time": data.total_mowing_time_minutes,
            "last_update": data.last_update,
            "status": data.status_description,
            "latitude": data.latitude,
            "longitude": data.longitude,
        }
        return values[key]

    @property
    def suggested_display_precision(self) -> int | None:
        """Return display precision for floating sensors."""
        if self.entity_description.key in {"latitude", "longitude"}:
            return 6
        return None

    @property
    def suggested_unit_of_measurement(self) -> str | None:
        """Return unit for coordinate display."""
        return None

    @property
    def should_poll(self) -> bool:
        """Use coordinator polling only."""
        return False

    @property
    def force_update(self) -> bool:
        """Avoid writing same state repeatedly."""
        return False

    @property
    def available(self) -> bool:
        """Return availability state."""
        return super().available and self.coordinator.data.online

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra sensor attributes."""
        if self.entity_description.key != "last_update":
            return {}

        return {
            "status": self.coordinator.data.status_description,
            "status_id": self.coordinator.data.status_id,
            "error": self.coordinator.data.error_description,
            "error_id": self.coordinator.data.error_id,
            "online": self.coordinator.data.online,
            "data_age": (
                datetime_age(self.coordinator.data.last_update)
                if self.coordinator.data.last_update
                else None
            ),
        }


def datetime_age(value: datetime) -> int:
    """Return the age of a UTC timestamp in whole seconds."""
    now = datetime.now(timezone.utc)
    delta = now - value.astimezone(timezone.utc)
    return max(0, int(delta.total_seconds()))
