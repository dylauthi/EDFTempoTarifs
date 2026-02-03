# EDF Tempo Tarifs Home Assistant Integration

Custom integration that pulls current EDF Tempo HC/HP tarifs via the API exposed at `https://www.api-couleur-tempo.fr/api/tarifs` and exposes them as `SensorEntity` values in Home Assistant.

## Installation
1. Copy the `custom_components/edf_tempo_tarifs` directory into your Home Assistant `config` folder if it does not already exist.
2. Restart Home Assistant so it detects the new integration.
3. Open Settings → Devices & Services → Add Integration and search for **Tarifs EDF Tempo**.
4. Enter an optional name and adjust the update interval (default 30 minutes, minimum 5 minutes).

## Entities
The integration creates six sensors (one for each color/HC/HP combination):
- `sensor.<name>_bleu_hc`
- `sensor.<name>_bleu_hp`
- `sensor.<name>_blanc_hc`
- `sensor.<name>_blanc_hp`
- `sensor.<name>_rouge_hc`
- `sensor.<name>_rouge_hp`

Each sensor uses `€/kWh`, the `monetary` device class, and exposes the API metadata attributes (`dateDebut`, `dateFin`, `dateMaj`, `tarifForce`, `dataGouvId`).

## Options
- **Intervalle de mise à jour** (minutes): frequency at which the integration polls the Tempo API (`update_interval`). Minimum 5 minutes.

## Future improvements
1. Add a sensor that exposes the current color label (Bleu/Blanc/Rouge) by calling `/api/now` or `/api/jourTempo/today`.
2. Add unit tests that mock the API to ensure parsing and attribute assignment.

_No automated tests are included yet; run Home Assistant's `hass --script check_config` after installation._
