"""Config flow for EDF Tempo Tarifs."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
    MIN_UPDATE_INTERVAL_MINUTES,
)


class TempoTarifConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EDF Tempo Tarifs."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        if user_input is not None:
            title = user_input.get(CONF_NAME, DEFAULT_NAME)
            return self.async_create_entry(
                title=title,
                data={CONF_NAME: title},
                options={
                    CONF_UPDATE_INTERVAL: user_input.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES
                    )
                },
            )

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=DEFAULT_UPDATE_INTERVAL_MINUTES,
                ): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL_MINUTES)
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        entry: config_entries.ConfigEntry,
    ) -> type[config_entries.OptionsFlow]:
        return TempoTarifOptionsFlow


class TempoTarifOptionsFlow(config_entries.OptionsFlow):
    """Handle options for EDF Tempo Tarifs."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.entry.options.get(
            CONF_UPDATE_INTERVAL,
            DEFAULT_UPDATE_INTERVAL_MINUTES,
        )

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=current_interval
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_UPDATE_INTERVAL_MINUTES),
                )
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
