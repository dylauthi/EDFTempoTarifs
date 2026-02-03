"""Sensor platform for EDF Tempo Tarifs."""
from __future__ import annotations

from dataclasses import dataclass
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
    TARIFS_SENSOR_KEYS,
    UNIT_EURO_PER_KWH,
)


@dataclass(frozen=True, kw_only=True)
class TempoSensorDescription(SensorEntityDescription):
    """Describes a Tempo sensor."""

    data_key: str
    value_key: str | None = None
    attribute_keys: tuple[str, ...] | None = None
    is_list: bool = False


SENSOR_DESCRIPTIONS: list[TempoSensorDescription] = [
    TempoSensorDescription(
        key=key,
        translation_key=translation_key,
        name=(
            "Tarif Tempo Bleu HC"
            if translation_key == "bleu_hc"
            else "Tarif Tempo Bleu HP"
            if translation_key == "bleu_hp"
            else "Tarif Tempo Blanc HC"
            if translation_key == "blanc_hc"
            else "Tarif Tempo Blanc HP"
            if translation_key == "blanc_hp"
            else "Tarif Tempo Rouge HC"
            if translation_key == "rouge_hc"
            else "Tarif Tempo Rouge HP"
        ),
        data_key="tarifs",
        value_key=key,
        attribute_keys=METADATA_ATTRIBUTES,
        native_unit_of_measurement=UNIT_EURO_PER_KWH,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.MEASUREMENT,
    )
    for key, translation_key in TARIFS_SENSOR_KEYS
]

SENSOR_DESCRIPTIONS.extend(
    [
        TempoSensorDescription(
            key="now_tarif_kwh",
            translation_key="now_tarif_kwh",
            name="Tarif Tempo actuel",
            data_key="now",
            value_key="libTarif",
            attribute_keys=(
                "tarifKwh",
                "codeCouleur",
                "codeHoraire",
                "applicableIn",
            ),
        ),
        TempoSensorDescription(
            key="now_tarif_kwh_value",
            translation_key="now_tarif_kwh_value",
            name="Tarif Tempo actuel (EUR/kWh)",
            data_key="now",
            value_key="tarifKwh",
            native_unit_of_measurement=UNIT_EURO_PER_KWH,
            device_class=SensorDeviceClass.MONETARY,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        TempoSensorDescription(
            key="jour_tempo_today",
            translation_key="jour_tempo_today",
            name="Couleur Tempo aujourd'hui",
            data_key="today",
            value_key="libCouleur",
            attribute_keys=("dateJour", "codeJour", "periode"),
        ),
        TempoSensorDescription(
            key="jour_tempo_tomorrow",
            translation_key="jour_tempo_tomorrow",
            name="Couleur Tempo demain",
            data_key="tomorrow",
            value_key="libCouleur",
            attribute_keys=("dateJour", "codeJour", "periode"),
        ),
        TempoSensorDescription(
            key="jour_tempo_yesterday",
            translation_key="jour_tempo_yesterday",
            name="Couleur Tempo hier",
            data_key="yesterday",
            value_key="libCouleur",
            attribute_keys=("dateJour", "codeJour", "periode"),
        ),
        TempoSensorDescription(
            key="tempo_stats",
            translation_key="tempo_stats",
            name="Statistiques Tempo",
            data_key="stats",
            value_key="periode",
            attribute_keys=(
                "bissextile",
                "dernierJourInclus",
                "joursBleusConsommes",
                "joursBlancsConsommes",
                "joursRougesConsommes",
                "joursBleusRestants",
                "joursBlancsRestants",
                "joursRougesRestants",
            ),
        ),
        TempoSensorDescription(
            key="tempo_24h",
            translation_key="tempo_24h",
            name="Prévisions Tempo 24h",
            data_key="24h",
            is_list=True,
        ),
    ]
)


async def async_setup_entry(
    hass, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the EDF Tempo Tarif sensors."""
    coordinator: TempoTarifCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TempoSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class TempoSensor(CoordinatorEntity, SensorEntity):
    """Representation of an EDF Tempo sensor."""

    def __init__(
        self,
        coordinator: TempoTarifCoordinator,
        entry: ConfigEntry,
        description: TempoSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_translation_key = description.translation_key
        self._attr_name = description.name
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
        description: TempoSensorDescription = self.entity_description
        data = self.coordinator.data.get(description.data_key)
        if data is None:
            return None
        try:
            if description.is_list:
                if isinstance(data, list):
                    return len(data)
                return None
            if description.value_key is None:
                return None
            value = data.get(description.value_key) if isinstance(data, dict) else None
            if value is None:
                return None
            if (
                description.device_class == SensorDeviceClass.MONETARY
                and description.native_unit_of_measurement == UNIT_EURO_PER_KWH
            ):
                return float(value)
            return value
        except (TypeError, ValueError):  # pragma: no cover
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return metadata attributes from the API payload."""
        description: TempoSensorDescription = self.entity_description
        data = self.coordinator.data.get(description.data_key)
        if data is None:
            return None
        attrs: dict[str, Any] = {}
        if description.is_list and isinstance(data, list):
            attrs["items"] = data
            return attrs
        if description.attribute_keys and isinstance(data, dict):
            for key in description.attribute_keys:
                value = data.get(key)
                if key == "tarifKwh" and value is not None:
                    attrs[key] = str(value)
                else:
                    attrs[key] = value
        return attrs or None
