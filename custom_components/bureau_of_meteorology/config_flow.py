"""Config flow for BOM."""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback

from .const import (
    CONF_FORECASTS_BASENAME,
    CONF_FORECASTS_CREATE,
    CONF_FORECASTS_DAYS,
    CONF_FORECASTS_MONITORED,
    CONF_OBSERVATIONS_BASENAME,
    CONF_OBSERVATIONS_CREATE,
    CONF_OBSERVATIONS_MONITORED,
    CONF_WARNINGS_BASENAME,
    CONF_WARNINGS_CREATE,
    CONF_WEATHER_NAME,
    DOMAIN,
    OBSERVATION_SENSOR_TYPES,
    FORECAST_SENSOR_TYPES,
    WARNING_SENSOR_TYPES,
)
from .PyBoM.collector import Collector

_LOGGER = logging.getLogger(__name__)


def _get_home_zone_coords(hass: HomeAssistant):
    """Get the current latitude and longitude from the home zone."""
    home_zone = hass.states.get("zone.home")
    if home_zone is not None:
        lat = home_zone.attributes.get("latitude")
        lon = home_zone.attributes.get("longitude")
        if lat is not None and lon is not None:
            return lat, lon
    # Fall back to HA core config if zone.home is unavailable
    _LOGGER.warning("BOM: zone.home not available, falling back to HA core location")
    return hass.config.latitude, hass.config.longitude


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BOM."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return BomOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        try:
            # Pull location from zone.home — no lat/lon form shown to the user
            lat, lon = _get_home_zone_coords(self.hass)

            self.collector = Collector(lat, lon, hass=self.hass)

            # Store lat/lon in data so __init__.py can read them on first setup
            self.data = {
                CONF_LATITUDE: lat,
                CONF_LONGITUDE: lon,
            }

            # Check if location is valid
            await self.collector.get_locations_data()
            if self.collector.locations_data is None:
                _LOGGER.debug("Unsupported location from zone.home")
                errors["base"] = "bad_location"
            else:
                # Populate observations and daily forecasts data
                await self.collector.async_update()

                # Move onto the next step of the config flow
                return await self.async_step_weather_name()

        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        # Only shown if something went wrong
        return self.async_show_form(step_id="user", errors=errors)

    async def async_step_weather_name(self, user_input=None):
        """Handle the locations step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WEATHER_NAME,
                    default=self.collector.locations_data["data"]["name"],
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                return await self.async_step_sensors_create()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="weather_name", data_schema=data_schema, errors=errors
        )

    async def async_step_sensors_create(self, user_input=None):
        """Handle the observations step."""
        data_schema = vol.Schema(
            {
                vol.Required(CONF_OBSERVATIONS_CREATE, default=True): bool,
                vol.Required(CONF_FORECASTS_CREATE, default=True): bool,
                vol.Required(CONF_WARNINGS_CREATE, default=True): bool,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_OBSERVATIONS_CREATE]:
                    return await self.async_step_observations_monitored()
                elif self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=self.collector.locations_data["data"]["name"],
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="sensors_create", data_schema=data_schema, errors=errors
        )

    async def async_step_observations_monitored(self, user_input=None):
        """Handle the observations monitored step."""
        monitored = {}
        for sensor in OBSERVATION_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OBSERVATIONS_BASENAME,
                    default=self.collector.observations_data["data"]["station"]["name"],
                ): str,
                vol.Required(CONF_OBSERVATIONS_MONITORED): cv.multi_select(monitored),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=self.collector.locations_data["data"]["name"],
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="observations_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_forecasts_monitored(self, user_input=None):
        """Handle the forecasts monitored step."""
        monitored = {}
        for sensor in FORECAST_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_FORECASTS_BASENAME,
                    default=self.collector.locations_data["data"]["name"],
                ): str,
                vol.Required(CONF_FORECASTS_MONITORED): cv.multi_select(monitored),
                vol.Required(CONF_FORECASTS_DAYS): vol.All(
                    vol.Coerce(int), vol.Range(0, 7)
                ),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                return self.async_create_entry(
                    title=self.collector.locations_data["data"]["name"], data=self.data
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="forecasts_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_warnings_basename(self, user_input=None):
        """Handle the warnings basename step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WARNINGS_BASENAME,
                    default=self.collector.locations_data["data"]["name"],
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                return self.async_create_entry(
                    title=self.collector.locations_data["data"]["name"], data=self.data
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="warnings_basename", data_schema=data_schema, errors=errors
        )


class BomOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialise the options flow."""
        super().__init__()
        self.data = {}

    async def async_step_init(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        try:
            # Pull location from zone.home — no lat/lon form shown to the user
            lat, lon = _get_home_zone_coords(self.hass)

            self.collector = Collector(lat, lon, hass=self.hass)

            self.data = {
                CONF_LATITUDE: lat,
                CONF_LONGITUDE: lon,
            }

            # Check if location is valid
            await self.collector.get_locations_data()
            if self.collector.locations_data is None:
                _LOGGER.debug("Unsupported location from zone.home")
                errors["base"] = "bad_location"
            else:
                # Populate observations and daily forecasts data
                await self.collector.async_update()

                return await self.async_step_weather_name()

        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        # Only shown if something went wrong
        return self.async_show_form(step_id="init", errors=errors)

    async def async_step_weather_name(self, user_input=None):
        """Handle the locations step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WEATHER_NAME,
                    default=self.config_entry.options.get(
                        CONF_WEATHER_NAME,
                        self.config_entry.data.get(
                            CONF_WEATHER_NAME,
                            self.collector.locations_data["data"]["name"],
                        ),
                    ),
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                return await self.async_step_sensors_create()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="weather_name", data_schema=data_schema, errors=errors
        )

    async def async_step_sensors_create(self, user_input=None):
        """Handle the observations step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OBSERVATIONS_CREATE,
                    default=self.config_entry.options.get(
                        CONF_OBSERVATIONS_CREATE,
                        self.config_entry.data.get(CONF_OBSERVATIONS_CREATE, True),
                    ),
                ): bool,
                vol.Required(
                    CONF_FORECASTS_CREATE,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_CREATE,
                        self.config_entry.data.get(CONF_FORECASTS_CREATE, True),
                    ),
                ): bool,
                vol.Required(
                    CONF_WARNINGS_CREATE,
                    default=self.config_entry.options.get(
                        CONF_WARNINGS_CREATE,
                        self.config_entry.data.get(CONF_WARNINGS_CREATE, True),
                    ),
                ): bool,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_OBSERVATIONS_CREATE]:
                    return await self.async_step_observations_monitored()
                elif self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=self.collector.locations_data["data"]["name"],
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="sensors_create", data_schema=data_schema, errors=errors
        )

    async def async_step_observations_monitored(self, user_input=None):
        """Handle the observations monitored step."""
        monitored = {}
        for sensor in OBSERVATION_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OBSERVATIONS_BASENAME,
                    default=self.config_entry.options.get(
                        CONF_OBSERVATIONS_BASENAME,
                        self.config_entry.data.get(
                            CONF_OBSERVATIONS_BASENAME,
                            self.collector.observations_data["data"]["station"]["name"],
                        ),
                    ),
                ): str,
                vol.Required(
                    CONF_OBSERVATIONS_MONITORED,
                    default=self.config_entry.options.get(
                        CONF_OBSERVATIONS_MONITORED,
                        self.config_entry.data.get(CONF_OBSERVATIONS_MONITORED, None),
                    ),
                ): cv.multi_select(monitored),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=self.collector.locations_data["data"]["name"],
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="observations_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_forecasts_monitored(self, user_input=None):
        """Handle the forecasts monitored step."""
        monitored = {}
        for sensor in FORECAST_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_FORECASTS_BASENAME,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_BASENAME,
                        self.config_entry.data.get(
                            CONF_FORECASTS_BASENAME,
                            self.collector.locations_data["data"]["name"],
                        ),
                    ),
                ): str,
                vol.Required(
                    CONF_FORECASTS_MONITORED,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_MONITORED,
                        self.config_entry.data.get(CONF_FORECASTS_MONITORED, None),
                    ),
                ): cv.multi_select(monitored),
                vol.Required(
                    CONF_FORECASTS_DAYS,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_DAYS,
                        self.config_entry.data.get(CONF_FORECASTS_DAYS, 0),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(0, 7)),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                return self.async_create_entry(
                    title=self.collector.locations_data["data"]["name"], data=self.data
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="forecasts_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_warnings_basename(self, user_input=None):
        """Handle the warnings basename step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WARNINGS_BASENAME,
                    default=self.config_entry.options.get(
                        CONF_WARNINGS_BASENAME,
                        self.config_entry.data.get(
                            CONF_WARNINGS_BASENAME,
                            self.collector.locations_data["data"]["name"],
                        ),
                    ),
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                return self.async_create_entry(
                    title=self.collector.locations_data["data"]["name"], data=self.data
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="warnings_basename", data_schema=data_schema, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
