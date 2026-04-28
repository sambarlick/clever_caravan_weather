# Clever Caravan Weather

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/sambarlick/clever_caravan_integrations.svg?style=for-the-badge)](https://github.com/sambarlick/clever_caravan_integrations/releases)
[![License](https://img.shields.io/github/license/sambarlick/clever_caravan_integrations.svg?style=for-the-badge)](LICENSE)
![Maintenance](https://img.shields.io/maintenance/yes/2026?style=for-the-badge)

A Home Assistant integration that pulls weather data from the [Australian Bureau of Meteorology (BOM)](http://www.bom.gov.au) for your **current** Home Zone location — built for caravan travellers who move around Australia.

> **This integration only supports locations within Australia.**

---

## What makes this different

Standard BOM integrations lock the weather location to the coordinates set at install time. This integration reads weather data for your **current `zone.home` location**, refreshing every 5 minutes. Move the caravan, update Home Zone, and weather follows you. No reconfiguration needed.

---

## Attribution

This integration is a fork of the excellent [bureau_of_meteorology](https://github.com/bremor/bureau_of_meteorology) custom component by [@bremor](https://github.com/bremor) and contributors. The BOM API client, sensor definitions, forecast formatting, and HA architecture are all their work. This fork adapts that foundation for dynamic Home Zone tracking and an opinionated one-click install.

---

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations** → **⋮** → **Custom Repositories**.
2. Add `https://github.com/sambarlick/clever_caravan_integrations` as a custom repository (category: Integration).
3. Install **Clever Caravan Weather** from the HACS store.
4. Restart Home Assistant.
5. Settings → Devices & Services → **+ Add Integration** → search **Clever Caravan Weather** → click. Done.

There are no setup questions. The integration reads `zone.home` automatically and creates all entities with the prefix `caravan_`.

### Manual

1. Copy the `custom_components/clever_caravan_weather` directory into your Home Assistant `config/custom_components/` folder.
2. Restart Home Assistant.
3. Add the integration as above.

---

## What you get

19 entities, all prefixed `caravan_`:

**Weather entities (2)**
- `weather.caravan` — daily forecast
- `weather.caravan_hourly` — hourly forecast

**Observations (6)**
- `sensor.caravan_temp` — current temperature
- `sensor.caravan_humidity`
- `sensor.caravan_dew_point`
- `sensor.caravan_wind_direction`
- `sensor.caravan_wind_speed_kilometre`
- `sensor.caravan_gust_speed_kilometre`

**Forecasts (8)**
- `sensor.caravan_short_text_0` through `sensor.caravan_short_text_7` — short text forecast for today (`_0`) and the next 7 days

**Warnings (1)**
- `sensor.caravan_warnings` — count of active BOM warnings; full warning list available in entity attributes

**Station debug (2)**
- `sensor.caravan_station` — name of the BOM observation station serving your location (e.g. "Brisbane Airport")
- `sensor.caravan_station_distance` — distance to that station, in km

The station sensors are useful when troubleshooting unusual weather readings — if the station is far away (e.g. >50 km), observations may not match what you're experiencing locally.

---

## How location tracking works

On every refresh cycle (every 5 minutes), the integration reads `zone.home`'s latitude and longitude. If the geohash of that location has changed since the last cycle, it invalidates the cached location data and fetches fresh BOM data for the new spot. All sensors and weather entities update accordingly.

To make this useful while travelling, set up an automation to update `zone.home` when your device location changes — for example using the Home Assistant Companion App's GPS, an OwnTracks tracker, or any GPS device integration.

---

## Troubleshooting

If sensors show `unavailable` or stale data, check the station distance — `sensor.caravan_station_distance`. If it's high, BOM doesn't have a close station for your current location.

For more detailed diagnostics, enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warn
  logs:
    custom_components.clever_caravan_weather: debug
```

---

## Notes & limitations

- Australia-only. Outside Australia the BOM API returns no data and install will fail.
- Weather data refreshes at most every 5 minutes (BOM rate limit).
- When `zone.home` moves, entity IDs and friendly names do **not** change — they stay as `caravan_*`. Only the data updates.
- There is no options/reconfigure flow. If you need to change something, delete and re-add the integration.

---

## Release notes

### v0.2.5 — Station debug sensors
- Added `sensor.caravan_station` (BOM station name) and `sensor.caravan_station_distance` (distance in km) for diagnostics.

### v0.2.2 — Curated sensor defaults
- Reduced from 60 entities to 17. Default install now creates only the most useful subset of observations and a single short-text forecast per day.

### v0.2.1 — One-click install
- Removed all setup questions. Reads `zone.home` automatically.
- Removed the options flow — reinstall to reconfigure.
- Default basename is `Caravan` (gives `weather.caravan`, `sensor.caravan_temp`, etc.).

### v0.1.0 — Initial fork
- Forked from [bureau_of_meteorology](https://github.com/bremor/bureau_of_meteorology).
- Replaced static lat/lon config with dynamic `zone.home` reads on every refresh cycle.

---

## Links

- **Repository:** [github.com/sambarlick/clever_caravan_integrations](https://github.com/sambarlick/clever_caravan_integrations)
- **Issues:** [github.com/sambarlick/clever_caravan_integrations/issues](https://github.com/sambarlick/clever_caravan_integrations/issues)
- **Upstream:** [github.com/bremor/bureau_of_meteorology](https://github.com/bremor/bureau_of_meteorology) by [@bremor](https://github.com/bremor)

---

*Part of the [Clever Caravan](https://github.com/sambarlick) project · Built on the work of [@bremor](https://github.com/bremor) and contributors · Data provided by the [Australian Bureau of Meteorology](http://www.bom.gov.au)*

## Integrations in this repo

- **Clever Caravan Weather** (`clever_caravan_weather`) — BoM weather that follows zone.home as the caravan moves.
- **Clever Caravan Location** (`clever_caravan_location`) — caravan GPS, speed, status, and health sensors.

Each is installed separately via HACS.
