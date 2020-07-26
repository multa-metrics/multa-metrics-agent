import schedule
import sys
import time
import traceback


from src.handlers.hardware_handler import get_shadow_data
from src.handlers.logging_handler import Logger
from src.handlers.mqtt_handler import (
    mqtt_connect_v2,
    mqtt_device_defender_publish_v2,
    mqtt_shadow_publish_v2,
    mqtt_shadow_update_subscribe_v2,
)
from src.handlers.registration_handler import RegistrationHandler, register_agent

from src.settings.app import DEVICE_NAME, DEVICE_SYNC_TIME
from src.settings.mqtt import DEVICE_DEFENDER_TOPIC

logs_handler = Logger()
logger = logs_handler.get_logger()


def test_job():
    logger.info(f"Job at {time.time()}")


if __name__ == "__main__":
    logger.info("Starting application!")

    try:
        if RegistrationHandler.check_credentials() is False:
            logger.info("Unable to find device credentials, starting registration...")
            register_agent()
        else:
            logger.info("Agent is already registered")

    except RuntimeError:
        logger.error("Error registering and saving credentials...")
        sys.exit(1)

    try:
        logger.info("Starting MQTT connection")
        mqtt_connection, shadow_client = mqtt_connect_v2()
    except Exception:
        logger.error("Error initalizing MQTT Connection... Exiting after a minute")
        logger.error(traceback.format_exc())
        time.sleep(60)
        sys.exit(1)

    try:
        logger.info("Starting Shadow Subscripitions")
        mqtt_shadow_update_subscribe_v2(shadow_client=shadow_client)
    except Exception:
        logger.error("Error subscribing to Shadow topics... Exiting after a minute")
        logger.error(traceback.format_exc())
        time.sleep(60)
        sys.exit(1)

    schedule.every(DEVICE_SYNC_TIME).seconds.do(
        mqtt_device_defender_publish_v2, mqtt_connection, topic=DEVICE_DEFENDER_TOPIC.format(device_name=DEVICE_NAME),
    )

    schedule.every(DEVICE_SYNC_TIME).seconds.do(
        mqtt_shadow_publish_v2, shadow_client=shadow_client, device_name=DEVICE_NAME, data=get_shadow_data()
    )

    while True:
        schedule.run_pending()
        time.sleep(1)
