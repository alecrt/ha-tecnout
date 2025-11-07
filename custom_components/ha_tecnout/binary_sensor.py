"""Binary sensor platform for TecnoAlarm TecnoOut integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up TecnoOut binary sensors from a config entry."""
    coordinator: TecnoOutCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for first data
    if not coordinator.data:
        return

    zones: list[ZoneDetailedStatus] = coordinator.data.get("zones", [])

    entities = []
    for zone in zones:
        # Only add enabled zones
        if zone.enabled:
            entities.append(TecnoOutZoneSensor(coordinator, zone.idx, entry))

    async_add_entities(entities)


class TecnoOutZoneSensor(CoordinatorEntity[TecnoOutCoordinator], BinarySensorEntity):
    """Representation of a TecnoOut Zone as a Binary Sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: TecnoOutCoordinator, zone_idx: int, entry: ConfigEntry
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._zone_idx = zone_idx
        self._attr_unique_id = f"{entry.entry_id}_zone_{zone_idx}"
        self._attr_translation_key = "zone"

        # Get zone data
        zone = self._get_zone()
        if zone and zone.description:
            self._attr_name = zone.description
        else:
            self._attr_name = f"Zone {zone_idx}"

    def _get_zone(self) -> ZoneDetailedStatus | None:
        """Get zone data from coordinator."""
        zones: list[ZoneDetailedStatus] = self.coordinator.data.get("zones", [])
        for zone in zones:
            if zone.idx == self._zone_idx:
                return zone
        return None

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on (zone is triggered)."""
        zone = self._get_zone()
        if zone is None:
            return None
        # Return True if zone has alarm or pre-alarm
        return zone.alarm or zone.pre_alarm

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._get_zone() is not None

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
            "zone_tamper_status": zone.zone_tamper_status,
            "zone_tamper_alarm": zone.zone_tamper_alarm,
            "battery_low": zone.battery_low,
            "supervision_alarm": zone.supervision_alarm,
            "active_zone": zone.active_zone,
            "learned_zone": zone.learned_zone,
            "mask_status": zone.mask_status,
            "fail_status": zone.fail_status,
            "alim_failure": zone.alim_failure,
            "pre_alarm": zone.pre_alarm,
            "alarm": zone.alarm,
            "alarm_24h": zone.alarm_24h,
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

