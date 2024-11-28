"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import TecnoalarmDataUpdateCoordinator
    from .lib import TecnoOutClient


type TecnoOutDataConfigEntry = ConfigEntry[TecnoOutData]


@dataclass
class TecnoOutData:
    """Data for the TecnoOUT integration."""

    client: TecnoOutClient
    coordinator: TecnoalarmDataUpdateCoordinator
    integration: Integration
