from confluent_kafka import Producer
import logging
from ..schemas.messages import MLResponse, MLError
from ..config.settings import app_settings

logger = logging.getLogger(__name__)


def _delivery_report(err, msg):
    if err:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")


class ResponseProducer:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': app_settings.KAFKA_BROKERS,
            'message.max.bytes': 10000000,
            'queue.buffering.max.messages': 100000,
            'queue.buffering.max.ms': 500,
            'compression.type': 'snappy',
        })

    def send_response(self, response: MLResponse):
        try:
            self.producer.produce(
                topic=app_settings.RESPONSE_TOPIC,
                key=response.request_id,
                value=response.model_dump_json(),
                callback=_delivery_report
            )
            self.producer.poll(0)
            logger.info(f"ResponseProducer:: Sent response for {response.request_id}")
        except Exception as e:
            logger.error(f"ResponseProducer:: Failed to send response: {e}")
            raise

    def send_error(self, error: MLError):
        try:
            self.producer.produce(
                topic=app_settings.ERROR_TOPIC,
                key=error.request_id,
                value=error.model_dump_json(),
                callback=_delivery_report
            )
            self.producer.poll(0)
            logger.error(f"ResponseProducer:: Sent error for {error.request_id}")
        except Exception as e:
            logger.error(f"ResponseProducer:: Failed to send error: {e}")
            raise

    def flush(self):
        self.producer.flush()
