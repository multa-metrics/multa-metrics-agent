import os

from awscrt import mqtt

DEVICE_ENDPOINT = os.environ.get("DEVICE_ENDPOINT", "adbf07ovrzhft-ats.iot.us-east-1.amazonaws.com")

DEVICE_CONNECTION_RETRY = os.environ.get("DEVICE_CONNECTION_RETRY")
DEVICE_CONNECTION_TIMEOUT = os.environ.get("DEVICE_CONNECTION_TIMEOUT")

COMMAND_ACTIONS_TOPIC = "cmd/actions/{device_name}/d2c"
TELEMETRY_PROCESSES_TOPIC = "tlm/processes/{device_name}/d2c"
TELEMETRY_SYSTEM_TOPIC = "tlm/system/{device_name}/d2c"

DEVICE_DEFENDER_TOPIC = "$aws/things/{device_name}/defender/metrics/json"

# DEVICE_CERTIFICATES_ROOT_DIRECTORY = os.environ.get("DEVICE_CERTIFICATES_ROOT_DIRECTORY", ".")
DEVICE_CERTIFICATES_ROOT_DIRECTORY = os.environ.get(
    "DEVICE_CERTIFICATES_ROOT_DIRECTORY", "/device/credentials/certificates"  # /device/credentials/certificates
)
DEVICE_PEM_FILE = f"{DEVICE_CERTIFICATES_ROOT_DIRECTORY}/certificate.pem"
DEVICE_PUBLIC_KEY_FILE = f"{DEVICE_CERTIFICATES_ROOT_DIRECTORY}/public_key.pub"
DEVICE_PRIVATE_KEY_FILE = f"{DEVICE_CERTIFICATES_ROOT_DIRECTORY}/private_key_key.priv"
ROOTCA_CERTIFICATE_FILE = f"{DEVICE_CERTIFICATES_ROOT_DIRECTORY}/root_ca.cert"

# DEVICE_DATA_DIRECTORY = os.environ.get("DEVICE_DATA_DIRECTORY", ".")
DEVICE_DATA_DIRECTORY = os.environ.get(
    "DEVICE_DATA_DIRECTORY", "/device/data"  # /device/credentials/certificates
)
DEVICE_DATA_FILE = f"{DEVICE_DATA_DIRECTORY}/device_data.json"

MQTT_QOS_SETTING = mqtt.QoS.AT_MOST_ONCE
MQTT_CONNECTION_RETURN_CODE_SETTING = mqtt.ConnectReturnCode.ACCEPTED
