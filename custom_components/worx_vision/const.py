"""Constants for the Worx Vision integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "worx_vision"

CONF_SERIAL_NUMBER = "serial_number"
CONF_CLOUD = "cloud"
DEFAULT_CLOUD = "worx"

PLATFORMS: list[Platform] = [
    Platform.LAWN_MOWER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]

UPDATE_INTERVAL = timedelta(seconds=30)

SERVICE_START_ZONE = "start_zone"
SERVICE_SET_SCHEDULE = "set_schedule"
SERVICE_OTS = "ots"

ATTR_ZONE = "zone"
ATTR_ENABLED = "enabled"
ATTR_ENTRIES = "entries"
ATTR_TIME_EXTENSION = "time_extension"
ATTR_BOUNDARY = "boundary"
ATTR_RUNTIME = "runtime"
