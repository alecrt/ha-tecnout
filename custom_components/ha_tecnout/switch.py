"""Switch platform for TecnoAlarm TecnoOut integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .tecnout.entities import (
    ProgramStatus,
    ProgramStatusEnum,
    SetProgramStatusEnum,
    ZoneDetailedStatus,
)

from .const import DOMAIN, MANUFACTURER
from .coordinator import TecnoOutCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TecnoOut switches from a config entry."""
    coordinator: TecnoOutCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for first data
    if not coordinator.data:
        return

    programs: list[ProgramStatus] = coordinator.data.get("programs", [])
    zones: list[ZoneDetailedStatus] = coordinator.data.get("zones", [])

    entities = []
    
    # Add program switches (exclude programs with default "Program X" name)
    for program in programs:
        # Skip programs that start with "Program" (not configured on the panel)
        if program.name and not program.name.startswith("Program"):
            entities.append(TecnoOutProgramSwitch(coordinator, program.idx, entry))
    
    # Add zone switches (only for enabled zones)
    for zone in zones:
        if zone.enabled:
            entities.append(TecnoOutZoneSwitch(coordinator, zone.idx, entry))

    async_add_entities(entities)


class TecnoOutProgramSwitch(CoordinatorEntity[TecnoOutCoordinator], SwitchEntity):
    """Representation of a TecnoOut Program as a Switch."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: TecnoOutCoordinator, program_idx: int, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._program_idx = program_idx
        self._attr_unique_id = f"{entry.entry_id}_program_{program_idx}"
        self._attr_translation_key = "program"

        # Get program data
        program = self._get_program()
        if program and program.name:
            self._attr_name = program.name
        else:
            self._attr_name = f"Program {program_idx}"

    def _get_program(self) -> ProgramStatus | None:
        """Get program data from coordinator."""
        programs: list[ProgramStatus] = self.coordinator.data.get("programs", [])
        for program in programs:
            if program.idx == self._program_idx:
                return program
        return None

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on (program is active)."""
        program = self._get_program()
        if program is None:
            return None
        # Program is on if not in STANDBY status
        return program.is_active

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._get_program() is not None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on (arm the program)."""
        try:
            await self.coordinator.async_set_program(
                self._program_idx, SetProgramStatusEnum.AUTOARM.value
            )
        except Exception as err:
            _LOGGER.error("Error turning on program %s: %s", self._program_idx, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off (disarm the program)."""
        try:
            await self.coordinator.async_set_program(
                self._program_idx, SetProgramStatusEnum.STANDBY.value
            )
        except Exception as err:
            _LOGGER.error("Error turning off program %s: %s", self._program_idx, err)
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
            "status": status_map.get(program.program_status, "Unknown"),
            "prealarm": program.prealarm,
            "alarm": program.alarm,
            "alarm_memory": program.alarm_memory,
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


class TecnoOutZoneSwitch(CoordinatorEntity[TecnoOutCoordinator], SwitchEntity):
    """Representation of a TecnoOut Zone as a Switch for isolation control."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: TecnoOutCoordinator, zone_idx: int, entry: ConfigEntry
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._zone_idx = zone_idx
        self._attr_unique_id = f"{entry.entry_id}_zone_switch_{zone_idx}"
        self._attr_translation_key = "zone_isolation"

        # Get zone data
        zone = self._get_zone()
        if zone and zone.description:
            self._attr_name = f"{zone.description} Isolation"
        else:
            self._attr_name = f"Zone {zone_idx} Isolation"

    def _get_zone(self) -> ZoneDetailedStatus | None:
        """Get zone data from coordinator."""
        zones: list[ZoneDetailedStatus] = self.coordinator.data.get("zones", [])
        for zone in zones:
            if zone.idx == self._zone_idx:
                return zone
        return None

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on (zone is active, not isolated)."""
        zone = self._get_zone()
        if zone is None:
            return None
        # Switch is ON when zone is ACTIVE (not isolated)
        # Switch is OFF when zone is ISOLATED
        return not zone.isolation_active

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._get_zone() is not None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on (reintegrate the zone - make it active)."""
        try:
            await self.coordinator.async_set_zone_isolation(
                self._zone_idx, isolate=False
            )
        except Exception as err:
            _LOGGER.error("Error reintegrating zone %s: %s", self._zone_idx, err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off (isolate the zone - make it inactive)."""
        try:
            await self.coordinator.async_set_zone_isolation(
                self._zone_idx, isolate=True
            )
        except Exception as err:
            _LOGGER.error("Error isolating zone %s: %s", self._zone_idx, err)
            raise

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        zone = self._get_zone()
        if zone is None:
            return {}

        return {
            "zone_number": zone.idx,
            "isolation_active": zone.isolation_active,
            "zone_status": zone.zone_status,
            "alarm": zone.alarm,
            "pre_alarm": zone.pre_alarm,
            "active_zone": zone.active_zone,
            "learned_zone": zone.learned_zone,
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

