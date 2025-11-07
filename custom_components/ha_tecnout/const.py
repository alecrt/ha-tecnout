"""Constants for the TecnoAlarm TecnoOut integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "ha_tecnout"

# Configuration
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_USER_CODE: Final = "user_code"
CONF_PASSPHRASE: Final = "passphrase"
CONF_LEGACY: Final = "legacy"
CONF_WATCHDOG_INTERVAL: Final = "watchdog_interval"
CONF_CONTROL_PIN: Final = "control_pin"

# Default values
DEFAULT_PORT: Final = 10001
DEFAULT_LEGACY: Final = False
DEFAULT_WATCHDOG_INTERVAL: Final = 30.0

# Services
SERVICE_ARM_PROGRAM: Final = "arm_program"
SERVICE_DISARM_PROGRAM: Final = "disarm_program"
ATTR_PROGRAM_ID: Final = "program_id"
ATTR_PIN: Final = "pin"

# Update interval
UPDATE_INTERVAL: Final = 1  # seconds - Fast polling for real-time zone updates

# Device info
MANUFACTURER: Final = "TecnoAlarm"
MODEL: Final = "TecnoOut"

