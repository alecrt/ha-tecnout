# sensor.py

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import (
    TecnoalarmDataUpdateCoordinator,
)
from .data import TecnoOutDataConfigEntry
from .lib import ZoneDetailedStatus
from .lib.entities import (
    GeneralStatus,
    ProgramStatus,
)

_LOGGER = logging.getLogger(__name__)


def _format_string(input_string: str) -> str:
    # Sostituisci gli underscore con spazi
    formatted_string = input_string.replace("_", " ")
    # Capitalizza ogni parola
    return formatted_string.title()


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: TecnoOutDataConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Configura i sensori."""
    coordinator = entry.runtime_data.coordinator
    entities = []

    # Sensori per le zone
    zones = coordinator.data.get("zones")
    if not zones:
        _LOGGER.warning("Nessuna zona trovata nei dati ricevuti.")
    else:
        entities.extend(
            [
                TecnoalarmZoneEntity(
                    coordinator,
                    zone,
                    zone.idx or idx,
                    zone.description or f"Zona {zone.idx or idx + 1}",
                )
                for idx, zone in enumerate(zones)
                if zone is not None and isinstance(zone, ZoneDetailedStatus)
            ]
        )
        entities.extend(
            [
                ZoneAttributeSensor(
                    coordinator,
                    zone,
                    attribute,
                    zone.idx or idx,
                    zone.description or f"Zona {zone.idx or idx + 1}",
                )
                for idx, zone in enumerate(zones)
                if zone is not None and isinstance(zone, ZoneDetailedStatus)
                for attribute in ["inLowBattery", "inFail"]
            ]
        )

    # Sensori per i programmi
    programs = coordinator.data.get("programs", [])
    if not programs:
        _LOGGER.debug("Nessun programma trovato nei dati ricevuti")
    else:
        for program in programs:
            if program is not None and isinstance(program, ProgramStatus):
                if program.idx is not None:
                    # Tentativo di recuperare il campo 'name' in vari formati
                    program.name = (
                        program.name
                        or f"Programma {program.idx}"  # Aggiungi +1 all'indice per la visualizzazione
                    )
                    entities.append(TecnoalarmProgramEntity(coordinator, program))

                    # Sensori individuali per prealarm, alarm, memAlarm, free
                    for attribute in ["prealarm", "alarm", "alarm_memory"]:
                        entities.extend(
                            [ProgramAttributeSensor(coordinator, program, attribute)]
                        )
                else:
                    _LOGGER.warning(
                        "Programma senza indice valido: %s, saltato", program
                    )
            else:
                _LOGGER.debug("Dato del programma %s è None e verrà ignorato", program)

    # Sensori per la centrale
    monitor = coordinator.data.get("monitor")
    if isinstance(monitor, GeneralStatus):
        # Tentativo di recuperare il campo 'description' della centrale, se presente
        centrale_description = monitor.control_panel_type or "Centrale"
        entities.append(TecnoalarmCentraleEntity(coordinator, centrale_description))

        # Creazione di sensori per ogni attributo della centrale
        for attribute in [
            "general_standby",
            "general_alarm_failure",
            "general_low_battery",
            "general_power_failure",
            "general_tamper",
            "wireless_failure",
            "hold_up_status",
            "program_alarm",
        ]:
            entities.extend(
                [CentraleAttributeSensor(coordinator, attribute, centrale_description)]
            )
    else:
        _LOGGER.warning("Nessun dato di tipo GeneralStatus trovato nei dati ricevuti")

    async_add_entities(entities, update_before_add=True)


class TecnoalarmZoneEntity(CoordinatorEntity, BinarySensorEntity):
    """Rappresenta una zona come entità separata."""

    def __init__(
        self,
        coordinator: TecnoalarmDataUpdateCoordinator,
        zone_data: ZoneDetailedStatus,
        zone_idx: int,
        description: str,
    ) -> None:
        """Inizializza la zona."""
        super().__init__(coordinator)
        self.zone_data = zone_data
        self.zone_idx = zone_idx
        self.description = description
        self._attr_name = description
        self._attr_unique_id = f"zone_{self.zone_idx}"
        self._attr_icon = "mdi:door"

    @property
    def state(self):
        """Ritorna lo stato della zona (OPEN/CLOSED)."""
        return self.zone_data.zone_status

    def _handle_coordinator_update(self):
        """Aggiorna lo stato della zona."""
        for zone in self.coordinator.data.get("zones", []):
            if (
                zone is not None
                and isinstance(zone, ZoneDetailedStatus)
                and zone.idx == self.zone_idx
            ):
                self.zone_data = zone
                break
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Informazioni sul dispositivo della zona."""
        return {
            "identifiers": {(DOMAIN, f"zone_{self.zone_idx}")},
            "name": self._attr_name,
            "manufacturer": "Tecnoalarm",
            "model": "Zone",
            "via_device": (DOMAIN, "tecnoalarm_hub"),
        }


class ZoneAttributeSensor(CoordinatorEntity, BinarySensorEntity):
    """Sensore per un attributo specifico della zona."""

    def __init__(
        self,
        coordinator: TecnoalarmDataUpdateCoordinator,
        zone_data: ZoneDetailedStatus,
        attribute: str,
        zone_idx: int,
        description: str,
    ) -> None:
        """Inizializza il sensore dell'attributo."""
        super().__init__(coordinator)
        self.zone_data = zone_data
        self.attribute = attribute
        self.zone_idx = zone_idx
        self.description = description
        self._attr_name = f"{description} {attribute}"  # Utilizza la description e l'attributo come nome
        self._attr_unique_id = f"zone_{self.zone_idx}_{attribute}"

        if attribute == "inLowBattery":
            self._attr_device_class = BinarySensorDeviceClass.BATTERY
        elif attribute == "inFail":
            self._attr_icon = "mdi:alert-circle-outline"

    @property
    def state(self) -> bool:
        """Ritorna il valore dell'attributo."""
        if self.attribute == "inLowBattery":
            return self.zone_data.battery_low
        if self.attribute == "inFail":
            return self.zone_data.fail_status
        return False

    def _handle_coordinator_update(self):
        """Aggiorna lo stato della zona."""
        for zone in self.coordinator.data.get("zones", []):
            if (
                zone is not None
                and isinstance(zone, ZoneDetailedStatus)
                and zone.idx == self.zone_idx
            ):
                self.zone_data = zone
                break
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Informazioni sul dispositivo della zona."""
        return {
            "identifiers": {(DOMAIN, f"zone_{self.zone_idx}")},
            "name": self.description,
            "manufacturer": "Tecnoalarm",
            "model": "Zone",
            "via_device": (DOMAIN, "tecnoalarm_hub"),
        }


class TecnoalarmProgramEntity(CoordinatorEntity, SensorEntity):
    """Rappresenta un programma come entità separata."""

    def __init__(self, coordinator, program_data: ProgramStatus) -> None:
        """Inizializza il programma."""
        super().__init__(coordinator)
        self.program_data = program_data
        self.idx = program_data.idx
        self.program_name = program_data.name
        self._attr_name = program_data.name  # Utilizza il nome del programma come nome
        self._attr_unique_id = f"program_{self.idx}"
        self._attr_icon = "mdi:shield-home"

    @property
    def state(self):
        """Ritorna lo stato del programma."""
        return self.program_data.program_status.name if self.program_data else "unknown"

    def _handle_coordinator_update(self) -> None:
        """Aggiorna lo stato del programma."""
        programs: list[ProgramStatus] = self.coordinator.data.get("programs", [])
        if self.idx < len(programs):
            self.program_data = programs[self.idx]
        else:
            _LOGGER.debug("Indice del programma %s fuori range", self.idx)
            # Mantiene lo stato precedente
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Informazioni sul dispositivo del programma."""
        return {
            "identifiers": {(DOMAIN, f"program_{self.idx}")},
            "name": self.program_name,
            "manufacturer": "Tecnoalarm",
            "model": "Program",
            "via_device": (DOMAIN, "tecnoalarm_hub"),
        }


class ProgramAttributeSensor(CoordinatorEntity, SensorEntity):
    """Sensore per un attributo specifico del programma."""

    def __init__(self, coordinator, program_data: ProgramStatus, attribute) -> None:
        """Inizializza il sensore dell'attributo."""
        super().__init__(coordinator)
        self.program_data = program_data
        self.idx = program_data.idx
        self.attribute = attribute
        self.program_name = program_data.name
        self._attr_name = f"{program_data.name} {attribute}"  # Utilizza il nome del programma e l'attributo come nome
        self._attr_unique_id = f"program_{self.idx}_{attribute}"

        if attribute == "prealarm":
            self._attr_icon = "mdi:alarm-light-outline"
        elif attribute == "alarm":
            self._attr_icon = "mdi:bell-alert"
        elif attribute == "alarm_memory":
            self._attr_icon = "mdi:bell-circle-outline"
        # elif attribute == "free":
        #     self._attr_icon = "mdi:check-circle-outline"

    @property
    def state(self):
        """Ritorna il valore dell'attributo."""
        return (
            self.program_data.to_dict().get(self.attribute, "unknown")
            if self.program_data
            else "unknown"
        )

    def _handle_coordinator_update(self) -> None:
        """Aggiorna lo stato del sensore."""
        programs = self.coordinator.data.get("programs", [])
        if self.idx < len(programs):
            self.program_data = programs[self.idx]
        else:
            _LOGGER.debug("Indice del programma %s fuori range.", self.idx)
            # Mantiene lo stato precedente
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Informazioni sul dispositivo del programma."""
        return {
            "identifiers": {(DOMAIN, f"program_{self.idx}")},
            "name": self.program_name,
            "manufacturer": "Tecnoalarm",
            "model": "Program",
            "via_device": (DOMAIN, "tecnoalarm_hub"),
        }


class TecnoalarmCentraleEntity(CoordinatorEntity, BinarySensorEntity):
    """Rappresenta la centrale come entità separata."""

    def __init__(self, coordinator, centrale_description) -> None:
        """Inizializza la centrale."""
        super().__init__(coordinator)
        self.centrale_description = centrale_description
        self._attr_name = (
            self.centrale_description
        )  # Utilizza la description della centrale come nome
        self._attr_unique_id = "centrale"
        self.monitor_data: GeneralStatus = self.coordinator.data.get("monitor", {})
        self._attr_icon = "mdi:home"

    @property
    def state(self):
        """Ritorna lo stato corrente della centrale."""
        return self.monitor_data.system_status_ok

    def _handle_coordinator_update(self):
        """Aggiorna lo stato della centrale."""
        self.monitor_data: GeneralStatus = self.coordinator.data.get("monitor", {})
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Informazioni sul dispositivo della centrale."""
        return {
            "identifiers": {(DOMAIN, "centrale")},
            "name": self.centrale_description,
            "manufacturer": "Tecnoalarm",
            "model": "Centrale",
            "via_device": (DOMAIN, "tecnoalarm_hub"),
        }


class CentraleAttributeSensor(CoordinatorEntity, BinarySensorEntity):
    """Sensore per un attributo specifico della centrale."""

    def __init__(self, coordinator, attribute, centrale_description) -> None:
        """Inizializza il sensore dell'attributo."""
        super().__init__(coordinator)
        self.attribute = attribute
        self.centrale_description = centrale_description
        self._attr_name = f"{self.centrale_description} {_format_string(attribute)}"  # Utilizza 'Centrale' e l'attributo come nome
        self._attr_unique_id = f"centrale_{attribute}"
        monitor = self.coordinator.data.get("monitor", {})
        if isinstance(monitor, GeneralStatus):
            self.monitor_data: dict = monitor.to_dict()

    @property
    def state(self):
        """Ritorna il valore dell'attributo."""
        return self.monitor_data.get(self.attribute, "unknown")

    def _handle_coordinator_update(self):
        """Aggiorna lo stato del sensore."""
        monitor = self.coordinator.data.get("monitor", {})
        if isinstance(monitor, GeneralStatus):
            self.monitor_data: dict = monitor.to_dict()
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Informazioni sul dispositivo della centrale."""
        return {
            "identifiers": {(DOMAIN, "centrale")},
            "name": self.centrale_description,
            "manufacturer": "Tecnoalarm",
            "model": "Centrale",
            "via_device": (DOMAIN, "tecnoalarm_hub"),
        }
