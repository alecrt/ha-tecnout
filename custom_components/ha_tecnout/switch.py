"""Switch platform for TecnoAlarm TecnoOut integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .tecnout.entities import ZoneDetailedStatus

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

    zones: list[ZoneDetailedStatus] = coordinator.data.get("zones", [])

    entities = []
    
    # Add zone switches (only for enabled zones)
    for zone in zones:
        if zone.enabled:
            entities.append(TecnoOutZoneSwitch(coordinator, zone.idx, entry))

    async_add_entities(entities)


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

