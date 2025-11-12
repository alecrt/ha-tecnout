"""Alarm Control Panel platform for TecnoAlarm TecnoOut integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    CodeFormat,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .tecnout.entities import (
    ProgramStatus,
    ProgramStatusEnum,
    SetProgramStatusEnum,
)

from .const import DOMAIN, MANUFACTURER, CONF_CONTROL_PIN
from .coordinator import TecnoOutCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TecnoOut alarm control panels from a config entry."""
    coordinator: TecnoOutCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for first data
    if not coordinator.data:
        return

    programs: list[ProgramStatus] = coordinator.data.get("programs", [])

    entities = []
    
    # Add alarm control panel for each program (exclude programs with default "Program X" name)
    for program in programs:
        # Skip programs that start with "Program" (not configured on the panel)
        if program.name and not program.name.startswith("Program"):
            entities.append(TecnoOutAlarmControlPanel(coordinator, program.idx, entry))

    async_add_entities(entities)


class TecnoOutAlarmControlPanel(CoordinatorEntity[TecnoOutCoordinator], AlarmControlPanelEntity):
    """Representation of a TecnoOut Program as an Alarm Control Panel."""

    _attr_has_entity_name = True
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_AWAY
    )

    def __init__(
        self, coordinator: TecnoOutCoordinator, program_idx: int, entry: ConfigEntry
    ) -> None:
        """Initialize the alarm control panel."""
        super().__init__(coordinator)
        self._program_idx = program_idx
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_alarm_program_{program_idx}"
        self._attr_translation_key = "alarm_program"

        # Get program data
        program = self._get_program()
        if program and program.name:
            self._attr_name = program.name
        else:
            self._attr_name = f"Program {program_idx}"

        # Configure PIN settings
        configured_pin = entry.data.get(CONF_CONTROL_PIN)
        if configured_pin:
            self._attr_code_format = CodeFormat.NUMBER
            self._attr_code_arm_required = True
        else:
            self._attr_code_format = None
            self._attr_code_arm_required = False

    def _get_program(self) -> ProgramStatus | None:
        """Get program data from coordinator."""
        programs: list[ProgramStatus] = self.coordinator.data.get("programs", [])
        for program in programs:
            if program.idx == self._program_idx:
                return program
        return None

    def _verify_code(self, code: str | None) -> bool:
        """Verify the provided code against the configured PIN."""
        configured_pin = self._entry.data.get(CONF_CONTROL_PIN)
        
        # If no PIN is configured, allow the action
        if not configured_pin:
            return True
        
        # If PIN is configured but not provided, deny
        if not code:
            return False
        
        # Verify code matches
        return code == configured_pin

    @property
    def state(self) -> str | None:
        """Return the state of the device."""
        program = self._get_program()
        if program is None:
            return None

        # Map TecnoOut status to alarm control panel states
        if program.program_status == ProgramStatusEnum.STANDBY:
            return "disarmed"
        elif program.program_status in (
            ProgramStatusEnum.ARMING_PHASE_EXCLUSION,
            ProgramStatusEnum.ARMING_PHASE_EXIT,
        ):
            return "arming"
        elif program.program_status == ProgramStatusEnum.ARMED:
            if program.alarm:
                return "triggered"
            return "armed_away"
        elif program.program_status == ProgramStatusEnum.PROGRAM_PARSET:
            return "armed_home"
        
        # Default to disarmed for unknown states
        return "disarmed"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._get_program() is not None

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        if not self._verify_code(code):
            raise ServiceValidationError(
                "Invalid PIN code",
                translation_domain=DOMAIN,
                translation_key="invalid_pin",
            )

        try:
            await self.coordinator.async_set_program(
                self._program_idx, SetProgramStatusEnum.STANDBY.value
            )
        except Exception as err:
            _LOGGER.error("Error disarming program %s: %s", self._program_idx, err)
            raise

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        if self._attr_code_arm_required and not self._verify_code(code):
            raise ServiceValidationError(
                "Invalid PIN code",
                translation_domain=DOMAIN,
                translation_key="invalid_pin",
            )

        try:
            await self.coordinator.async_set_program(
                self._program_idx, SetProgramStatusEnum.AUTOARM.value
            )
        except Exception as err:
            _LOGGER.error("Error arming program %s: %s", self._program_idx, err)
            raise

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        program = self._get_program()
        if program is None:
            return {}

        # Get human-readable status
        status_map = {
            ProgramStatusEnum.STANDBY: "Standby",
            ProgramStatusEnum.ARMING_PHASE_EXCLUSION: "Arming (Exclusion)",
            ProgramStatusEnum.ARMING_PHASE_EXIT: "Arming (Exit)",
            ProgramStatusEnum.ARMED: "Armed",
            ProgramStatusEnum.END_OF_BYPASS: "End of Bypass",
            ProgramStatusEnum.PROGRAM_PARSET: "Partial Set",
            ProgramStatusEnum.END_OF_BYPASS_SIGNALING: "End of Bypass Signaling",
        }

        return {
            "program_number": program.idx,
            "detailed_status": status_map.get(program.program_status, "Unknown"),
            "prealarm": program.prealarm,
            "alarm": program.alarm,
            "alarm_memory": program.alarm_memory,
            "is_active": program.is_active,
        }

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        general_status = self.coordinator.data.get("general_status")
        device_name = (
            general_status.control_panel_type if general_status else "TecnoAlarm"
        )

        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": device_name,
            "manufacturer": MANUFACTURER,
            "model": general_status.control_panel_type if general_status else "Unknown",
            "sw_version": (
                general_status.firmware_release if general_status else None
            ),
        }

