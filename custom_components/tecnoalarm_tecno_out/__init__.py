# __init__.py

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_loaded_integration

from custom_components.tecnoalarm_tecno_out.data import TecnoOutData
from custom_components.tecnoalarm_tecno_out.lib.tecnout_client import TecnoOutClient

from .const import (
    CENTRALE_SERIE_TP,
    CONF_CODE,
    CONF_HOST,
    CONF_MODELLO_CENTRALE,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    CONF_TOKEN,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)
from .coordinator import TecnoalarmDataUpdateCoordinator
from .data import TecnoOutDataConfigEntry

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(
    hass: HomeAssistant, entry: TecnoOutDataConfigEntry
) -> bool:
    """Configura il componente da una ConfigEntry."""
    coordinator = TecnoalarmDataUpdateCoordinator(
        hass, entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    )

    entry.runtime_data = TecnoOutData(
        client=TecnoOutClient(
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
            entry.data[CONF_CODE],
            entry.data[CONF_TOKEN],
            entry.data.get(CONF_MODELLO_CENTRALE) == CENTRALE_SERIE_TP,
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: TecnoOutDataConfigEntry
) -> bool:
    """Gestisce la rimozione del componente."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: TecnoOutDataConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
