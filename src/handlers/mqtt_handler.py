from concurrent.futures import Future
import json
import time
import sys
import traceback

from AWSIoTDeviceDefenderAgentSDK import collector
from awscrt import io, mqtt
from awsiot import iotshadow, mqtt_connection_builder

# from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from src.handlers.logging_handler import Logger
from src.settings.app import DEVICE_NAME
from src.settings.mqtt import (
    DEVICE_ENDPOINT,
    DEVICE_PEM_FILE,
    DEVICE_PRIVATE_KEY_FILE,
    MQTT_CONNECTION_RETURN_CODE_SETTING,
    MQTT_QOS_SETTING,
    ROOTCA_CERTIFICATE_FILE,
)

logs_handler = Logger()
logger = logs_handler.get_logger()


def mqtt_publish_v2(mqtt_connection_object_v2, topic: str, payload: dict):
    logger.info("Publishing to AWS IoT")
    try:
        mqtt_connection_object_v2.publish(topic=topic, payload=json.dumps(payload), qos=MQTT_QOS_SETTING)
    except Exception:
        logger.error("Error publishing to AWS IoT!")
        logger.error(traceback.format_exc())
        return False
    else:
        return True


def mqtt_device_defender_publish_v2(mqtt_connection_object_v2, topic: str):
    logger.info("Publishing to AWS IoT")
    metrics_collector = collector.Collector(short_metrics_names=False)
    metric = metrics_collector.collect_metrics()
    try:
        mqtt_connection_object_v2.publish(topic=topic, payload=metric.to_json_string(), qos=MQTT_QOS_SETTING)
    except Exception:
        logger.error("Error publishing to AWS IoT!")
        logger.error(traceback.format_exc())
        return False
    else:
        return True


def mqtt_shadow_publish_v2(shadow_client, device_name, data):
    logger.info("Updating AWS IoT Device Shadow...")
    try:
        shadow_client.publish_update_shadow(
            request=iotshadow.UpdateShadowRequest(thing_name=device_name, state=iotshadow.ShadowState(reported=data,)),
            qos=MQTT_QOS_SETTING,
        )
    except Exception:
        logger.error("Error updating AWS IoT Device shadow")
        logger.error(traceback.format_exc())
        return False
    else:
        return True


def mqtt_shadow_update_subscribe_v2(shadow_client):
    logger.info("Subscribing to Update responses...")
    try:
        update_accepted_subscribed_future, _ = shadow_client.subscribe_to_update_shadow_accepted(
            request=iotshadow.UpdateShadowSubscriptionRequest(thing_name=DEVICE_NAME),
            qos=MQTT_QOS_SETTING,
            callback=MqttClientV2.on_update_shadow_accepted,
        )

        update_rejected_subscribed_future, _ = shadow_client.subscribe_to_update_shadow_rejected(
            request=iotshadow.UpdateShadowSubscriptionRequest(thing_name=DEVICE_NAME),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=MqttClientV2.on_update_shadow_rejected,
        )

        # Wait for subscriptions to succeed
        update_accepted_subscribed_future.result()
        update_rejected_subscribed_future.result()
    except Exception:
        logger.error("Error subscribing to Shadow Actions")
        logger.error(traceback.format_exc())
        return False
    else:
        return True


def mqtt_connect_v2():
    while True:
        mqtt_agent = MqttClientV2()
        mqttconnection, shadow_client = mqtt_agent.connect()
        if mqttconnection is False:
            logger.error("Error connecting to AWS IoT using MQTT device SDK")
            time.sleep(60)
        else:
            logger.info("Successfully connected to AWS IoT")
            return mqttconnection, shadow_client


class MqttClientV2:
    def __init__(self):
        self.event_loop_group = io.EventLoopGroup(1)
        self.host_resolver = io.DefaultHostResolver(self.event_loop_group)
        self.client_bootstrap = io.ClientBootstrap(self.event_loop_group, self.host_resolver)
        self.mqtt_connection = None

    def connect(self):
        try:
            logger.info("Setting MQTT connection parameters to AWS IoT")
            mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=DEVICE_ENDPOINT,
                cert_filepath=DEVICE_PEM_FILE,
                pri_key_filepath=DEVICE_PRIVATE_KEY_FILE,
                client_bootstrap=self.client_bootstrap,
                ca_filepath=ROOTCA_CERTIFICATE_FILE,
                on_connection_interrupted=self.on_connection_interrupted,
                on_connection_resumed=self.on_connection_resumed,
                client_id=DEVICE_NAME,
                clean_session=False,
                keep_alive_secs=6,
            )

            logger.info(f"Connecting to AWS IoT endpoint {DEVICE_ENDPOINT} with client ID: {DEVICE_NAME}")
            connect_future = mqtt_connection.connect()

            logger.info("Initializing AWS IoT Shadow client")
            shadow_client = iotshadow.IotShadowClient(mqtt_connection)

            logger.info("Waiting for connection result...")
            connect_future.result()
            logger.info("Connected!!!")

            return mqtt_connection, shadow_client

        except Exception:
            logger.error("Error connecting using MQTT IoT SDK V2")
            logger.error(traceback.format_exc())
            return False

    @staticmethod
    def shadow_subscribe(shadow_client):
        logger.info("Subscribing to Update responses...")
        update_accepted_subscribed_future, _ = shadow_client.subscribe_to_update_shadow_accepted(
            request=iotshadow.UpdateShadowSubscriptionRequest(thing_name=DEVICE_NAME),
            qos=MQTT_QOS_SETTING,
            callback=MqttClientV2.on_update_shadow_accepted,
        )

        update_rejected_subscribed_future, _ = shadow_client.subscribe_to_update_shadow_rejected(
            request=iotshadow.UpdateShadowSubscriptionRequest(thing_name=DEVICE_NAME),
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=MqttClientV2.on_update_shadow_rejected,
        )

        # Wait for subscriptions to succeed
        update_accepted_subscribed_future.result()
        update_rejected_subscribed_future.result()

    # Callback when connection is accidentally lost.
    @staticmethod
    def on_connection_interrupted(connection, error, **kwargs):
        logger.info("Connection interrupted. error: {}".format(error))

    # Callback when an interrupted connection is re-established.
    @staticmethod
    def on_connection_resumed(connection, return_code, session_present, **kwargs):
        logger.info("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

        if return_code == MQTT_CONNECTION_RETURN_CODE_SETTING and not session_present:
            logger.info("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(MqttClientV2.on_resubscribe_complete)

    @staticmethod
    def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        logger.info("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results["topics"]:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))

    # Callback when the subscribed topic receives a message
    @staticmethod
    def on_message_received(topic, payload, **kwargs):
        logger.info("Received message from topic '{}': {}".format(topic, payload))

    @staticmethod
    def on_update_shadow_accepted(response):
        # type: (iotshadow.UpdateShadowResponse) -> None
        try:
            logger.info(
                "Finished updating reported shadow value to '{}'.".format(response.state.reported)
            )  # type: ignore
        except Exception:
            logger.error(traceback.format_exc())
            exit("Updated shadow is missing the target property.")

    @staticmethod
    def on_update_shadow_rejected(error):
        # type: (iotshadow.ErrorResponse) -> None
        exit("Update request was rejected. code:{} message:'{}'".format(error.code, error.message))

    @staticmethod
    def on_publish_update_shadow(future):
        # type: (Future) -> None
        try:
            future.result()
            logger.info("Update request published.")
        except Exception as e:
            logger.error("Failed to publish update request.")
            exit(e)
