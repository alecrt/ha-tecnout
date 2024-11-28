"""TecnoOutEntity class."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import TecnoalarmDataUpdateCoordinator


class TecnoOutCoordinatorEntity(CoordinatorEntity[TecnoalarmDataUpdateCoordinator]):
    """TecnoOutEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: TecnoalarmDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
