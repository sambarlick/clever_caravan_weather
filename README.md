# 🚐 Clever Caravan Weather

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/sambarlick/clever_caravan_weather.svg?style=for-the-badge)](https://github.com/sambarlick/clever_caravan_weather/releases)
[![License](https://img.shields.io/github/license/sambarlick/clever_caravan_weather.svg?style=for-the-badge)](LICENSE)
![Maintenance](https://img.shields.io/maintenance/yes/2026?style=for-the-badge)

A Home Assistant integration that pulls weather data from the [Australian Bureau of Meteorology (BOM)](http://www.bom.gov.au) for your **current** Home Zone location — built for caravan travellers who move around Australia.

> **This integration only supports locations within Australia.**

---

## What makes this different

Standard BOM integrations lock the weather location to the coordinates set at install time. This integration reads weather data for your **current `zone.home` location**, refreshing every 5 minutes. Move the caravan, update Home Zone, and weather follows you. No reconfiguration needed.

---

## Attribution

This integration is a fork of the excellent [bureau_of_meteorology](https://github.com/bremor/bureau_of_meteorology) custom component by [@bremor](https://github.com/bremor) and contributors. The BOM API client, sensor definitions, forecast formatting, and HA architecture are all their work.

---

## 📥 Installation

### HACS (recommended)

1. Open **HACS** in Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add your repository URL: `https://github.com/sambarlick/clever_caravan_weather`
4. Select **Integration** as the category and click **Add**.
5. Install **Clever Caravan Weather** from the HACS store and restart Home Assistant.

---

## 📡 Sensor Overview

| Sensor | Description |
|--------|-------------|
| **weather.caravan** | Daily and Hourly forecasts. |
| **sensor.caravan_temp** | Current observation temperature. |
| **sensor.caravan_warnings** | Count of active BOM warnings. |
| **sensor.caravan_station** | Name and distance of the serving BOM station. |

---

## Links

- **Repository:** [github.com/sambarlick/clever_caravan_weather](https://github.com/sambarlick/clever_caravan_weather)
- **Issues:** [github.com/sambarlick/clever_caravan_weather/issues](https://github.com/sambarlick/clever_caravan_weather/issues)

---

*Part of the [Clever Caravan](https://github.com/sambarlick) project · Data provided by the [Australian Bureau of Meteorology](http://www.bom.gov.au)*
