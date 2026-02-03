"""Sensor platform for EDF Tempo Tarifs."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TempoTarifCoordinator
from .const import (
    DEFAULT_NAME,
    DOMAIN,
    METADATA_ATTRIBUTES,
    SENSOR_KEYS,
    UNIT_EURO_PER_KWH,
)


SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key=key,
        translation_key=translation_key,
        native_unit_of_measurement=UNIT_EURO_PER_KWH,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
    )
    for key, translation_key in SENSOR_KEYS
]


async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the EDF Tempo Tarif sensors."""
    coordinator: TempoTarifCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TarifSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class TarifSensor(CoordinatorEntity, SensorEntity):
    """Representation of a EDF Tempo Tarif sensor."""

    def __init__(self, coordinator: TempoTarifCoordinator, entry: ConfigEntry, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_translation_key = description.translation_key
        self._attr_name = entry.title or DEFAULT_NAME
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title or DEFAULT_NAME,
            manufacturer="EDF",
            model="Tempo Tarifs API",
        )

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):  # pragma: no cover
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return metadata attributes from the API payload."""
        data = self.coordinator.data
        if not data:
            return None
        attrs = {
            key: data.get(key) for key in METADATA_ATTRIBUTES if key in data
        }
        return attrs or None
