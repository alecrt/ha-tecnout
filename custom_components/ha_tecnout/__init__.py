"""The TecnoAlarm TecnoOut integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_ARM_PROGRAM,
    SERVICE_DISARM_PROGRAM,
    ATTR_PROGRAM_ID,
    ATTR_PIN,
    CONF_CONTROL_PIN,
)
from .coordinator import TecnoOutCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]

# Service schemas
SERVICE_PROGRAM_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PROGRAM_ID): cv.positive_int,
        vol.Optional(ATTR_PIN): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TecnoAlarm TecnoOut from a config entry."""
    coordinator = TecnoOutCoordinator(hass, entry)

    # Perform first refresh
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass, entry, coordinator)

    return True


async def async_setup_services(
    hass: HomeAssistant, entry: ConfigEntry, coordinator: TecnoOutCoordinator
) -> None:
    """Set up services for the integration."""
    
    def verify_pin(provided_pin: str | None) -> bool:
        """Verify if the provided PIN matches the configured one."""
        configured_pin = entry.data.get(CONF_CONTROL_PIN)
        
        # If no PIN is configured, allow the action
        if not configured_pin:
            return True
        
        # If PIN is configured but not provided, deny
        if not provided_pin:
            return False
        
        # Verify PIN matches
        return provided_pin == configured_pin

    async def handle_arm_program(call: ServiceCall) -> None:
        """Handle arm program service call."""
        program_id = call.data[ATTR_PROGRAM_ID]
        provided_pin = call.data.get(ATTR_PIN)
        
        if not verify_pin(provided_pin):
            raise HomeAssistantError("Invalid or missing PIN")
        
        _LOGGER.info("Arming program %s via service", program_id)
        await coordinator.async_set_program(program_id, 1)  # AUTOARM

    async def handle_disarm_program(call: ServiceCall) -> None:
        """Handle disarm program service call."""
        program_id = call.data[ATTR_PROGRAM_ID]
        provided_pin = call.data.get(ATTR_PIN)
        
        if not verify_pin(provided_pin):
            raise HomeAssistantError("Invalid or missing PIN")
        
        _LOGGER.info("Disarming program %s via service", program_id)
        await coordinator.async_set_program(program_id, 0)  # STANDBY

    # Register services only if not already registered
    if not hass.services.has_service(DOMAIN, SERVICE_ARM_PROGRAM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_ARM_PROGRAM,
            handle_arm_program,
            schema=SERVICE_PROGRAM_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_DISARM_PROGRAM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_DISARM_PROGRAM,
            handle_disarm_program,
            schema=SERVICE_PROGRAM_SCHEMA,
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Shutdown coordinator
        coordinator: TecnoOutCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_shutdown()

        # Remove coordinator
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

