# Clever Caravan Weather Custom Component

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/sambarlick/bureau_of_meteorology.svg?style=for-the-badge)](https://github.com/sambarlick/bureau_of_meteorology/releases)
[![License](https://img.shields.io/github/license/sambarlick/bureau_of_meteorology.svg?style=for-the-badge)](LICENSE)
![Maintenance](https://img.shields.io/maintenance/yes/2025?style=for-the-badge)

A Home Assistant custom integration that provides Australian weather data from the Bureau of Meteorology (BOM), adapted for travellers and caravan enthusiasts who move around Australia.

### **This integration only supports locations within Australia.**

This Home Assistant custom component uses the [Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for weather information.

What makes this different
Standard BOM integrations lock the weather location to the coordinates set at install time. This fork is built for people on the move — it reads weather data for your current Home Zone location, not where you were when you first set it up.
Update your Home Zone (via an automation, a companion app, or manually) and the integration automatically pulls weather data for wherever you are now. No reconfiguration needed.

Attribution
This integration is a fork of the excellent bureau_of_meteorology custom component originally created by @bremor and contributors. The core data fetching, sensor definitions, forecast formatting, and HA integration architecture are all their work. This fork adapts that foundation to use dynamic Home Zone location tracking.

Installation
Manual

Copy the custom_components/clever_caravan_weather directory into your Home Assistant custom_components folder.
Restart Home Assistant.

HACS (Custom Repository)

In HACS, go to Integrations → Custom Repositories.
Add https://github.com/sambarlick/bureau_of_meteorology as a custom repository (category: Integration).
Install Clever Caravan Weather from the HACS store.
Restart Home Assistant.


Configuration
After installation:

Go to Settings → Devices & Services.
Click + Add Integration and search for Clever Caravan Weather.
Click through the setup — no location entry required. The integration reads your Home Zone automatically.


How location tracking works
On every refresh cycle (every 5 minutes), the integration checks the latitude and longitude of your zone.home entity. If the location has changed since the last check, it derives a new BOM location geohash and fetches fresh weather data for that area.
To make this useful while travelling, set up an automation to update zone.home when your device location changes — for example using the Home Assistant Companion App's GPS or a GPS tracker integration.

Troubleshooting
Enable debug logging by adding the following to your configuration.yaml:
yamllogger:
  default: warn
  logs:
    custom_components.clever_caravan_weather: debug

Notes

Weather data will not refresh faster than once every 5 minutes.
When your Home Zone location changes, sensor entity IDs retain their original names (based on the suburb at install time). The data they report will be correct for the new location even if the name hasn't updated.
This integration only works within Australia.


Links

Repository: https://github.com/sambarlick/bureau_of_meteorology
Issue Tracker: https://github.com/sambarlick/bureau_of_meteorology/issues
Original integration by @bremor: https://github.com/bremor/bureau_of_meteorology


Built for Clever Caravan · Based on the work of @bremor and contributors · Data provided by the Australian Bureau of Meteorology
