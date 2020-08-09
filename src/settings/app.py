import os

AGENT_VERSION = os.environ.get("AGENT_VERSION", "0.0.4")

DEVICE_NAME = os.environ.get("DEVICE_NAME")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", os.environ.get("DEFAULT_DEVICE_TYPE"))
DEVICE_TYPE_ATTRIBUTES = os.environ.get("DEVICE_TYPE_ATTRIBUTES", {})
API_KEY = os.environ.get("API_KEY")

DEVICE_SYNC_TIME = int(os.environ.get("DEVICE_SYNC_TIME", "60"))
