"""Config flow for Worx Vision integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pyworxcloud import WorxCloud

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import CONF_CLOUD, CONF_SERIAL_NUMBER, DEFAULT_CLOUD, DOMAIN

_LOGGER = logging.getLogger(__name__)


class WorxVisionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Worx Vision."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow state."""
        self._input: dict[str, Any] = {}
        self._mowers: dict[str, str] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial credentials step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cloud = user_input.get(CONF_CLOUD, DEFAULT_CLOUD)
            client = WorxCloud(
                user_input[CONF_EMAIL],
                user_input[CONF_PASSWORD],
                cloud=cloud,
            )

            try:
                await client.authenticate()
                await client.connect()

                self._mowers = {
                    str(getattr(device, "serial_number", "")): str(
                        getattr(device, "name", "Unknown mower")
                    )
                    for device in client.devices.values()
                }
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Worx Vision login failed: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                try:
                    await client.disconnect()
                except Exception:  # noqa: BLE001
                    pass

            if not errors:
                if not self._mowers:
                    errors["base"] = "no_devices"
                elif len(self._mowers) == 1:
                    serial = next(iter(self._mowers.keys()))
                    await self.async_set_unique_id(serial)
                    self._abort_if_unique_id_configured()
                    data = {
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_CLOUD: cloud,
                        CONF_SERIAL_NUMBER: serial,
                    }
                    return self.async_create_entry(
                        title=self._mowers[serial],
                        data=data,
                    )
                else:
                    self._input = user_input
                    return await self.async_step_select_mower()

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_CLOUD, default=DEFAULT_CLOUD): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_select_mower(self, user_input: dict[str, Any] | None = None):
        """Handle mower selection when multiple devices are available."""
        errors: dict[str, str] = {}

        if user_input is not None:
            serial = user_input[CONF_SERIAL_NUMBER]
            await self.async_set_unique_id(serial)
            self._abort_if_unique_id_configured()

            data = {
                CONF_EMAIL: self._input[CONF_EMAIL],
                CONF_PASSWORD: self._input[CONF_PASSWORD],
                CONF_CLOUD: self._input.get(CONF_CLOUD, DEFAULT_CLOUD),
                CONF_SERIAL_NUMBER: serial,
            }
            return self.async_create_entry(title=self._mowers[serial], data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_SERIAL_NUMBER): vol.In(self._mowers),
            }
        )

        return self.async_show_form(
            step_id="select_mower",
            data_schema=schema,
            errors=errors,
        )
