"""Constants for the Worx Vision integration."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from homeassistant.const import Platform

DOMAIN = "worx_vision"
INTEGRATION_VERSION: str = json.loads(
    (Path(__file__).parent / "manifest.json").read_text()
)["version"]
FRONTEND_CARD_FILENAME = "worx-vision-card.js"
FRONTEND_CARD_URL_PATH = f"/{DOMAIN}"
FRONTEND_CARD_MODULE_URL = f"{FRONTEND_CARD_URL_PATH}/{FRONTEND_CARD_FILENAME}"
DATA_FRONTEND_CARD_REGISTERED = f"{DOMAIN}_frontend_card_registered"
DATA_STATIC_PATH_REGISTERED = f"{DOMAIN}_static_path_registered"

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
