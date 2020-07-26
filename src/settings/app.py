import os

AGENT_VERSION = os.environ.get("AGENT_VERSION")

DEVICE_NAME = os.environ.get("DEVICE_NAME", "test")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", os.environ.get("DEFAULT_DEVICE_TYPE"))
DEVICE_TYPE_ATTRIBUTES = os.environ.get("DEVICE_TYPE_ATTRIBUTES", {})
ACCOUNT_TOKEN = os.environ.get("ACCOUNT_TOKEN", "test")

DEVICE_SYNC_TIME = os.environ.get("DEVICE_SYNC_TIME", 60)
