"""Config flow for TecnoAlarm TecnoOut integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .tecnout.tecnout_client import TecnoOutClient

from .const import (
    CONF_USER_CODE,
    CONF_PASSPHRASE,
    CONF_LEGACY,
    CONF_WATCHDOG_INTERVAL,
    CONF_CONTROL_PIN,
    DEFAULT_PORT,
    DEFAULT_LEGACY,
    DEFAULT_WATCHDOG_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_USER_CODE): int,
        vol.Optional(CONF_PASSPHRASE, default=""): str,
        vol.Optional(CONF_LEGACY, default=DEFAULT_LEGACY): bool,
        vol.Optional(
            CONF_WATCHDOG_INTERVAL, default=DEFAULT_WATCHDOG_INTERVAL
        ): vol.Coerce(float),
        vol.Optional(CONF_CONTROL_PIN): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Create client WITHOUT watchdog for connection test
    # Watchdog will be enabled only when integration is fully set up
    client = TecnoOutClient(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        user_code=data[CONF_USER_CODE],
        passphrase=data.get(CONF_PASSPHRASE, "") or "",
        legacy=data.get(CONF_LEGACY, DEFAULT_LEGACY),
        watchdog_interval=None,  # Disable watchdog during config flow test
    )

    try:
        await hass.async_add_executor_job(client.connect)
        info = await hass.async_add_executor_job(client.get_info)
    except ConnectionError as err:
        raise CannotConnect from err
    except Exception as err:
        _LOGGER.exception("Unexpected exception")
        raise InvalidAuth from err
    finally:
        # Always close the client, even if there's an error
        try:
            await hass.async_add_executor_job(client.close)
        except Exception:
            pass  # Ignore errors during cleanup

    # Return info that you want to store in the config entry.
    return {
        "title": f"TecnoAlarm {info.panel_type}",
        "panel_type": info.panel_type,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TecnoAlarm TecnoOut."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create unique ID based on host and port
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

