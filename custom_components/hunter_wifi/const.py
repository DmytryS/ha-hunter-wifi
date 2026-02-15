"""Constants for Hunter WiFi irrigation integration."""

from typing import Final

DOMAIN: Final = "hunter_wifi"
TITLE: Final = "Hunter WiFi"

CONF_HOST: Final = "host"
CONF_DEVICE_NAME: Final = "device_name"
CONF_ZONES: Final = "zones"
CONF_PROGRAMS: Final = "programs"

ATTR_ZONE: Final = "zone"
ATTR_PROGRAM: Final = "program"
ATTR_TIME: Final = "time"

DEFAULT_ZONE_DURATION_MINUTES: Final = 5
DEFAULT_DEVICE_NAME: Final = "Hunter WiFi"
MIN_ZONE = 1
MAX_ZONE = 8
MIN_PROGRAM = 1
MAX_PROGRAM = 3
