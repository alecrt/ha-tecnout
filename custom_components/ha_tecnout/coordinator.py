"""DataUpdateCoordinator for TecnoAlarm TecnoOut integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .tecnout.tecnout_client import TecnoOutClient
from .tecnout.entities import GeneralStatus, ZoneDetailedStatus, ProgramStatus

from .const import (
    CONF_HOST,
    CONF_PORT,
    CONF_USER_CODE,
    CONF_PASSPHRASE,
    CONF_LEGACY,
    CONF_WATCHDOG_INTERVAL,
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class TecnoOutCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching TecnoOut data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.entry = entry
        self.client: TecnoOutClient | None = None
        self._zones_count: int = 0
        self._programs_count: int = 0
        self._zones_descriptions: list[str] = []
        self._programs_descriptions: list[str] = []

    async def _async_setup(self) -> None:
        """Set up the client and get initial info."""
        try:
            self.client = TecnoOutClient(
                host=self.entry.data[CONF_HOST],
                port=self.entry.data[CONF_PORT],
                user_code=self.entry.data[CONF_USER_CODE],
                passphrase=self.entry.data[CONF_PASSPHRASE],
                legacy=self.entry.data.get(CONF_LEGACY, False),
                watchdog_interval=self.entry.data.get(CONF_WATCHDOG_INTERVAL),
            )

            await self.hass.async_add_executor_job(self.client.connect)

            # Get control panel info to know zones and programs count
            info = await self.hass.async_add_executor_job(self.client.get_info)
            self._zones_count = info.associated_zones
            self._programs_count = info.programs_count

            _LOGGER.info(
                "TecnoOut connected: %s zones, %s programs",
                self._zones_count,
                self._programs_count,
            )

            # Get zones and programs descriptions
            if self._zones_count > 0:
                self._zones_descriptions = await self.hass.async_add_executor_job(
                    self.client.get_zones_description, self._zones_count
                )

            if self._programs_count > 0:
                self._programs_descriptions = await self.hass.async_add_executor_job(
                    self.client.get_programs_description, self._programs_count
                )

        except Exception as err:
            _LOGGER.error("Error connecting to TecnoOut: %s", err)
            raise ConfigEntryNotReady(f"Error connecting to TecnoOut: {err}") from err

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from TecnoOut."""
        if self.client is None:
            await self._async_setup()

        try:
            # Get general status
            general_status: GeneralStatus = await self.hass.async_add_executor_job(
                self.client.get_general_status
            )

            # Get zones detailed status
            zones: list[ZoneDetailedStatus] = []
            if self._zones_count > 0:
                zones = await self.hass.async_add_executor_job(
                    self.client.get_zones_detail, self._zones_count
                )
                # Add descriptions to zones
                for zone in zones:
                    if zone.idx <= len(self._zones_descriptions):
                        zone.description = self._zones_descriptions[zone.idx - 1]

            # Get programs status
            programs: list[ProgramStatus] = []
            if self._programs_count > 0:
                programs = await self.hass.async_add_executor_job(
                    self.client.get_programs_status, self._programs_count
                )
                # Add descriptions to programs
                for program in programs:
                    if program.idx <= len(self._programs_descriptions):
                        program.name = self._programs_descriptions[program.idx - 1]

            return {
                "general_status": general_status,
                "zones": zones,
                "programs": programs,
            }

        except Exception as err:
            _LOGGER.error("Error fetching TecnoOut data: %s", err)
            raise UpdateFailed(f"Error communicating with TecnoOut: {err}") from err

    async def async_set_program(self, program_idx: int, status: int) -> None:
        """Set program status."""
        if self.client is None:
            raise UpdateFailed("Client not initialized")

        try:
            from .tecnout.entities import SetProgramStatusEnum

            await self.hass.async_add_executor_job(
                self.client.set_program, program_idx, SetProgramStatusEnum(status)
            )
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting program status: %s", err)
            raise UpdateFailed(f"Error setting program status: {err}") from err

    async def async_set_zone_isolation(
        self, zone_number: int, isolate: bool
    ) -> None:
        """Set zone isolation status."""
        if self.client is None:
            raise UpdateFailed("Client not initialized")

        try:
            await self.hass.async_add_executor_job(
                self.client.set_zone_isolation, zone_number, isolate
            )
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting zone isolation: %s", err)
            raise UpdateFailed(f"Error setting zone isolation: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self.client:
            await self.hass.async_add_executor_job(self.client.close)
            self.client = None

