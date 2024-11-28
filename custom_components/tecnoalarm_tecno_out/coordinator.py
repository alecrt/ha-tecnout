# coordinator.py

import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_POLL_INTERVAL,
    DOMAIN,
)

from .lib.entities import (
    GeneralStatus,
    ProgramStatus,
    SetProgramStatusEnum,
    ZoneDetailedStatus,
)

from .const import DOMAIN
from .data import TecnoOutDataConfigEntry
from homeassistant.core import HomeAssistant


_LOGGER = logging.getLogger(__name__)


class TecnoalarmDataUpdateCoordinator(DataUpdateCoordinator):
    """Gestisce il fetching dei dati dalle API Tecnoalarm."""

    config_entry: TecnoOutDataConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Inizializza il coordinatore."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
            always_update=False,
        )
        self._programs_name: list[str] = []
        self._valid_programs_count = 0
        self._zones_dscr: list[str] = []

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        self._client = self.config_entry.runtime_data.client
        self._client.connect()
        self._info = self._client.get_info()

        self._programs_name = self._client.get_programs_description(
            self._info.programs_count
        )

        self._zones_dscr = self._client.get_zones_description(self._info.max_zones)

    async def _async_update_data(self):
        """Fetch data from tecnoOUT endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        retries = 3
        for attempt in range(retries):
            try:
                monitor = self._client.get_general_status()

                enabled_zones = []
                zones = self._client.get_zones_detail(self._info.max_zones)
                for zone in zones:
                    if zone.enabled:
                        zone.description = self._zones_dscr[zone.idx - 1]
                        enabled_zones.append(zone)

                programs = self._client.get_programs_status(self._info.programs_count)
                for prg in programs:
                    prg.name = self._programs_name[prg.idx - 1]

                data = TecnoOutCoordinatorData(enabled_zones, programs, monitor)
                _LOGGER.debug("Dati aggiornati: %s", data)
                return data

            except ConnectionError as e:
                if attempt < retries - 1:
                    _LOGGER.warning("Errore durante la connessione al server: %s", e)
                    _LOGGER.warning("Retrying...")
                    await asyncio.sleep(5)  # Attendi 5 secondi prima di riprovare
                    self._client.connect()
                else:
                    raise UpdateFailed(
                        f"Failed to fetch data after {retries} attempts"
                    ) from e
            except UpdateFailed as e:
                msg = f"Errore durante l'aggiornamento dei dati: {e}"
                _LOGGER.error(msg)
                raise UpdateFailed(msg) from e
            except Exception as e:
                _LOGGER.exception("Eccezione in _async_update_data")
                msg = f"Eccezione durante l'aggiornamento dei dati: {e}"
                raise UpdateFailed(msg) from e
        return None

    def set_program_status(self, idx: int, status: SetProgramStatusEnum):
        """Set the status of a program.

        Args:
            idx (int): The index of the program.
            status (ProgramStatusEnum): The status to set for the program.

        """
        self._client.set_program(idx, status)


class TecnoOutCoordinatorData:
    """Class to hold the data fetched from TecnoOut and compare using hash."""

    def __init__(
        self,
        zones: list[ZoneDetailedStatus],
        programs: list[ProgramStatus],
        monitor: GeneralStatus,
    ) -> None:
        """Initialize the TecnoOutCoordinatorData.

        Args:
            zones (list[ZoneDetailedStatus]): List of zone detailed statuses.
            programs (list[ProgramStatus]): List of program statuses.
            monitor (GeneralStatus): General status monitor.

        """
        self.zones = zones
        self.programs = programs
        self.monitor = monitor

    def get(self, attribute: str, default_value=None) -> object:  # noqa: D102
        if attribute == "zones":
            return self.zones
        if attribute == "programs":
            return self.programs
        if attribute == "monitor":
            return self.monitor
        return default_value

    def __str__(self) -> str:  # noqa: D105
        return (
            f"Monitor: {self.monitor}, Zones: {self.zones}, Programs: {self.programs}"
        )

    def __eq__(self, other: object) -> bool:
        """Check if two TecnoOutCoordinatorData objects are equal."""
        test = (
            isinstance(other, TecnoOutCoordinatorData)
            and hash(self.monitor) == hash(other.monitor)
            and hash(tuple(self.zones)) == hash(tuple(other.zones))
            and hash(tuple(self.programs)) == hash(tuple(other.programs))
        )
        return test
