"""Constants for the EDF Tempo Tarifs integration."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "edf_tempo_tarifs"
PLATFORMS = ["sensor"]
DEFAULT_NAME = "EDF Tempo Tarifs"
DEFAULT_UPDATE_INTERVAL_MINUTES = 30
MIN_UPDATE_INTERVAL_MINUTES = 5
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=DEFAULT_UPDATE_INTERVAL_MINUTES)
CONF_UPDATE_INTERVAL = "update_interval"
TARIFS_ENDPOINT = "https://www.api-couleur-tempo.fr/api/tarifs"
REQUEST_TIMEOUT = 10
UNIT_EURO_PER_KWH = "€/kWh"
SENSOR_KEYS = (
    ("bleuHC", "bleu_hc"),
    ("bleuHP", "bleu_hp"),
    ("blancHC", "blanc_hc"),
    ("blancHP", "blanc_hp"),
    ("rougeHC", "rouge_hc"),
    ("rougeHP", "rouge_hp"),
)
METADATA_ATTRIBUTES = (
    "dateDebut",
    "dateFin",
    "dateMaj",
    "tarifForce",
    "dataGouvId",
)
