"""EDF Tempo Tarifs integration entrypoint."""
from __future__ import annotations

import asyncio
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
    API_ENDPOINTS,
    PLATFORMS,
    REQUEST_TIMEOUT,
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

    async def _fetch_json(self, url: str) -> Any:
        """Fetch JSON data from a Tempo API endpoint."""
        async with async_timeout.timeout(REQUEST_TIMEOUT):
            response = await self._session.get(url)
            if response.status != 200:
                raise UpdateFailed(
                    f"Unexpected response {response.status} from Tempo API"
                )
            return await response.json()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from all Tempo API endpoints."""
        tasks = {
            name: self._fetch_json(url) for name, url in API_ENDPOINTS.items()
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        payload: dict[str, Any] = {}
        errors: list[str] = []
        for (name, _), result in zip(tasks.items(), results):
            if isinstance(result, Exception):
                errors.append(name)
                continue
            payload[name] = result

        if not payload:
            raise UpdateFailed("Fetching EDF Tempo data failed")
        if errors:
            _LOGGER.warning("Tempo API partial update failed for: %s", ", ".join(errors))
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
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
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
