"""Constants for the ThingsBoard integration."""
from datetime import timedelta

DOMAIN = "thingsboard"

# Configuration
CONF_HOST = "host"
CONF_ACCESS_TOKEN = "access_token"

# Defaults
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
DEFAULT_NAME = "ThingsBoard"

# API Endpoints
API_TELEMETRY = "/api/v1/{token}/telemetry"
API_ATTRIBUTES = "/api/v1/{token}/attributes"
API_ATTRIBUTES_REQUEST = "/api/v1/{token}/attributes?clientKeys={client_keys}&sharedKeys={shared_keys}"

# Attributes
ATTR_LAST_UPDATE = "last_update"
ATTR_DEVICE_TYPE = "device_type"
