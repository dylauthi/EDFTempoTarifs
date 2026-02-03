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
API_BASE_URL = "https://www.api-couleur-tempo.fr/api"
REQUEST_TIMEOUT = 10
UNIT_EURO_PER_KWH = "EUR/kWh"
TARIFS_SENSOR_KEYS = (
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
API_ENDPOINTS = {
    "tarifs": f"{API_BASE_URL}/tarifs",
    "now": f"{API_BASE_URL}/now",
    "24h": f"{API_BASE_URL}/24h",
    "today": f"{API_BASE_URL}/jourTempo/today",
    "tomorrow": f"{API_BASE_URL}/jourTempo/tomorrow",
    "yesterday": f"{API_BASE_URL}/jourTempo/yesterday",
    "stats": f"{API_BASE_URL}/stats",
}
