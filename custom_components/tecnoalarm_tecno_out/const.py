"""Constants for tecnoOUT integration."""

from logging import Logger, getLogger

DOMAIN = "tecnoalarm_tecno_out"
DEFAULT_POLL_INTERVAL = 5  # in seconds

CONF_HOST = "host"
CONF_PORT = "port"
CONF_TOKEN = "token"  # noqa: S105
CONF_CODE = "code"
CONF_POLL_INTERVAL = "poll_interval"
CONF_MODELLO_CENTRALE = "modello_centrale"
CONF_NOME = "nome"

CENTRALE_SERIE_TP = "Serie TP"
CENTRALE_SERIE_EV = "Serie EV"

LOGGER: Logger = getLogger(__package__)
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
