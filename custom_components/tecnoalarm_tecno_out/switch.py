# switch.py

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.tecnoalarm_tecno_out.entity import TecnoOutCoordinatorEntity

from .const import DOMAIN
from .coordinator import TecnoalarmDataUpdateCoordinator
from .data import TecnoOutDataConfigEntry
from .lib import (
    ProgramStatus,
    ProgramStatusEnum,
    SetProgramStatusEnum,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: TecnoOutDataConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configura gli switch per i programmi."""
    coordinator = entry.runtime_data.coordinator
    entities = []

    # Sensori per i programmi
    programs = coordinator.data.get("programs", [])
    if not programs:
        _LOGGER.debug("Nessun programma trovato nei dati ricevuti")
    else:
        for program in programs:
            if program is not None and isinstance(program, ProgramStatus):
                if program.idx is not None:
                    entities.append(TecnoalarmProgramSwitch(coordinator, program))
                else:
                    _LOGGER.warning(
                        "Programma senza indice valido: %s, saltato", program
                    )
            else:
                _LOGGER.debug("Dato del programma è None e verrà ignorato")

    # Aggiungi gli switch
    async_add_entities(entities, update_before_add=True)


class TecnoalarmProgramSwitch(TecnoOutCoordinatorEntity, SwitchEntity):
    """Rappresenta uno switch per un programma."""

    def __init__(
        self, coordinator: TecnoalarmDataUpdateCoordinator, program_data: ProgramStatus
    ) -> None:
        """Inizializza lo switch."""
        super().__init__(coordinator)
        self.program_data = program_data
        self.idx = program_data.idx
        self.program_name = program_data.name or f"Programma {program_data.idx}"
        self._attr_name = self.program_name  # Utilizza il nome del programma come nome
        self._attr_unique_id = f"program_switch_{self.idx}"
        self._attr_icon = "mdi:shield-home"

    @property
    def is_on(self) -> bool:
        """Ritorna True se il programma è armato o parzializzato."""
        if self.program_data.program_status.value is not None:
            return self.program_data.program_status in (
                ProgramStatusEnum.ARMED,
                ProgramStatusEnum.PROGRAM_PARSET,
            )

        _LOGGER.debug(
            "Dati del programma mancanti o non validi per il programma %s", self.idx
        )
        return False

    async def async_turn_on(self, **_: Any) -> None:
        """Attiva il programma."""
        await self._change_program_state(SetProgramStatusEnum.ARMED)
        await (
            self.coordinator.async_request_refresh()
        )  # Richiedi un aggiornamento immediato

    async def async_turn_off(self, **_: Any) -> None:
        """Disattiva il programma."""
        await self._change_program_state(SetProgramStatusEnum.STANDBY)
        await (
            self.coordinator.async_request_refresh()
        )  # Richiedi un aggiornamento immediato

    async def _change_program_state(self, state: SetProgramStatusEnum) -> None:
        try:
            self.coordinator.set_program_status(self.idx, state)
        except Exception as e:
            _LOGGER.error(
                "Errore durante la modifica dello stato del programma %s: %s",
                self.idx,
                e,
            )

    def _handle_coordinator_update(self) -> None:
        """Aggiorna lo stato dello switch."""
        programs = self.coordinator.data.get("programs", [])
        if self.idx < len(programs):
            self.program_data = programs[self.idx]
            _LOGGER.debug(
                "Aggiornamento switch del programma %s: %s", self.idx, self.is_on
            )
        else:
            _LOGGER.debug("Indice del programma %s fuori range", self.idx)
            # Mantiene lo stato precedente
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Ritorna le informazioni del dispositivo a cui appartiene lo switch."""
        return {
            "identifiers": {(DOMAIN, f"program_{self.idx}")},
            "name": self.program_name,
            "manufacturer": "Tecnoalarm",
            "model": "Program",
            "via_device": (DOMAIN, "tecnoalarm_hub"),
        }
