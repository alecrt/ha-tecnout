"""Gestisce il flusso di configurazione per Tecnoalarm Tecnout."""

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import (
    CENTRALE_SERIE_EV,
    CENTRALE_SERIE_TP,
    CONF_CODE,
    CONF_HOST,
    CONF_MODELLO_CENTRALE,
    CONF_NOME,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    CONF_TOKEN,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)


class TecnoalarmConfigFlow(ConfigFlow, domain=DOMAIN):
    """Gestisce il flusso di configurazione per Tecnoalarm Tecnout."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Passo iniziale dove l'utente inserisce i dati."""
        errors = {}

        if user_input is not None:
            # Verifica se esiste già una configurazione con lo stesso seriale
            existing_entries = [
                entry
                for entry in self._async_current_entries()
                if entry.data.get(CONF_NOME) == user_input[CONF_NOME]
            ]
            if existing_entries:
                errors["base"] = "serial_exists"
            else:
                if not user_input.get(CONF_TOKEN):
                    user_input[CONF_TOKEN] = ""
                return self.async_create_entry(
                    title=user_input[CONF_NOME], data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NOME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=vol.Coerce(int)(10102)): int,
                vol.Required(CONF_CODE): int,
                vol.Optional(CONF_TOKEN): str,
                vol.Required(CONF_MODELLO_CENTRALE): vol.In(
                    [CENTRALE_SERIE_TP, CENTRALE_SERIE_EV]
                ),
                vol.Optional(
                    CONF_POLL_INTERVAL, default=vol.Coerce(int)(DEFAULT_POLL_INTERVAL)
                ): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the reconfigure flow step."""
        config_entry = self.hass.config_entries.async_get_entry(
            self.context.get("entry_id", "")
        )
        if config_entry is None:
            return self.async_abort(reason="missing_configuration")

        name = config_entry.data.get(CONF_NOME)

        if user_input is not None:
            await self.async_set_unique_id(config_entry.unique_id)
            self._abort_if_unique_id_mismatch()
            if not user_input.get(CONF_TOKEN):
                user_input[CONF_TOKEN] = ""
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NOME, default=vol.Coerce(str)(name)): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=vol.Coerce(int)(10102)): int,
                vol.Required(CONF_CODE): int,
                vol.Optional(CONF_TOKEN): str,
                vol.Required(CONF_MODELLO_CENTRALE): vol.In(
                    [CENTRALE_SERIE_TP, CENTRALE_SERIE_EV]
                ),
                vol.Optional(
                    CONF_POLL_INTERVAL, default=vol.Coerce(int)(DEFAULT_POLL_INTERVAL)
                ): int,
            }
        )
        return self.async_show_form(step_id="reconfigure", data_schema=data_schema)
