import json
import requests
import time
import traceback

from src.settings.app import API_KEY, AGENT_VERSION, DEVICE_NAME
from src.settings.registration import *
from src.settings.mqtt import DEVICE_PEM_FILE, DEVICE_PRIVATE_KEY_FILE, DEVICE_PUBLIC_KEY_FILE, ROOTCA_CERTIFICATE_FILE
from src.handlers.logging_handler import Logger

logs_handler = Logger()
logger = logs_handler.get_logger()


def register_agent():
    while True:
        registration_data = RegistrationHandler.register()
        if isinstance(registration_data, dict):
            credentials_status = RegistrationHandler.save_credentials(
                credentials_dictionary=registration_data["certificates"], root_ca=registration_data["rootCA"]
            )
            if credentials_status is False:
                RegistrationHandler.clean_credentials()
                raise RuntimeError
            else:
                logger.info("Registration was successful!")
                break
        elif registration_data is False:
            logger.error("Registration failed! Retrying in a minute...")
            time.sleep(60)
        else:
            time.sleep(60)


class RegistrationHandler:
    def __init__(self):
        pass

    @staticmethod
    def register():
        data = dict(thingName=DEVICE_NAME, version=AGENT_VERSION)
        headers = {"Authorization": f"ApiKey {API_KEY}", "Content-Type": "application/json"}
        try:
            response = requests.post(url=DEVICE_CONFIGURATION_URL, data=json.dumps(data), headers=headers)
            response.raise_for_status()
        except requests.HTTPError:
            logger.error("Something went wrong with registration...")
            if response.status_code == 400:
                logger.error("Invalid data passed when creating thing...")
                logger.error(response.json().get("error"))
                return False
            elif response.status_code == 401:
                logger.error(
                    "Device registration is unauthorized... Check if your account has reached maximum number of agents"
                )
                logger.error(response.json().get("error"))
                return False
            elif response.status_code == 500:
                logger.error("Something went wrong during registration...")
                logger.error(response.json().get("error"))
                return False
            else:
                return None
        except Exception:
            logger.error("Uncaptured error...")
            logger.error(traceback.format_exc())
            return None
        else:
            logger.info("Registration was successful!")
            return response.json()

    @staticmethod
    def save_credentials(credentials_dictionary, root_ca):
        try:
            logger.info("Saving certificate files...")
            with open(DEVICE_PEM_FILE, "w") as pem_certificate_file:
                pem_certificate_file.write(credentials_dictionary["pem"])
            with open(DEVICE_PRIVATE_KEY_FILE, "w") as private_key_file:
                private_key_file.write(credentials_dictionary["key_pair"]["private_key"])
            with open(DEVICE_PUBLIC_KEY_FILE, "w") as public_key_file:
                public_key_file.write(credentials_dictionary["key_pair"]["public_key"])
            with open(ROOTCA_CERTIFICATE_FILE, "w") as root_ca_file:
                root_ca_file.write(root_ca)
        except Exception:
            logger.error("Error saving certificate files...")
            logger.error(traceback.format_exc())
            return False
        else:
            logger.info("Certificates saved correctly")
            return True

    @staticmethod
    def check_credentials():
        # TODO: ADD CREDENTIALS CHECKS BEFORE REGISTERING
        if (
            os.path.isfile(DEVICE_PEM_FILE)
            and os.path.isfile(DEVICE_PRIVATE_KEY_FILE)
            and os.path.isfile(DEVICE_PUBLIC_KEY_FILE)
            and os.path.isfile(ROOTCA_CERTIFICATE_FILE)
        ):
            return True
        else:
            return False

    @staticmethod
    def clean_credentials():
        # TODO: ADD CREDENTIALS REMOVAL IF PROCESS EXITS UNEXPECTEDLY
        try:
            os.remove(DEVICE_PEM_FILE)
        except Exception:
            logger.error(traceback.format_exc())

        try:
            os.remove(DEVICE_PRIVATE_KEY_FILE)
        except Exception:
            logger.error(traceback.format_exc())

        try:
            os.remove(DEVICE_PUBLIC_KEY_FILE)
        except Exception:
            logger.error(traceback.format_exc())

        try:
            os.remove(ROOTCA_CERTIFICATE_FILE)
        except Exception:
            logger.error(traceback.format_exc())
