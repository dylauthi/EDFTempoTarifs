"""EDF Tempo Tarifs integration entrypoint."""
from __future__ import annotations

import logging

import async_timeout
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    PLATFORMS,
    REQUEST_TIMEOUT,
    TARIFS_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class TempoTarifCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that fetches EDF Tempo tarifs."""

    def __init__(self, hass: HomeAssistant, update_interval, name: str):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )
        self._session = aiohttp_client.async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, float]:
        """Fetch data from the Tempo API."""
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(TARIFS_ENDPOINT)
                if response.status != 200:
                    raise UpdateFailed(
                        f"Unexpected response {response.status} from Tempo API"
                    )
                payload = await response.json()
        except UpdateFailed:
            raise
        except Exception as err:  # pragma: no cover - network errors
            raise UpdateFailed("Fetching EDF Tempo tarifs failed") from err
        return payload


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EDF Tempo Tarifs from a config entry."""
    update_minutes = entry.options.get(
        CONF_UPDATE_INTERVAL, int(DEFAULT_UPDATE_INTERVAL.total_seconds() / 60)
    )
    try:
        update_interval = timedelta(minutes=int(update_minutes))
    except Exception:  # pragma: no cover - fallback
        update_interval = DEFAULT_UPDATE_INTERVAL

    entry_name = entry.data.get(CONF_NAME, entry.title or DEFAULT_NAME)
    coordinator = TempoTarifCoordinator(hass, update_interval, entry_name)
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        _LOGGER.warning("Initial fetch failed: %s", err)
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Legacy setup, required for YAML compatibility stub."""
    hass.data.setdefault(DOMAIN, {})
    return True
