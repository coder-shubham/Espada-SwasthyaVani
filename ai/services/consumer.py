import json
from confluent_kafka import Consumer, KafkaException
import logging
from schemas.messages import MLRequest, MLError
from config.settings import app_settings
from services.processor import process_request
from services.producer import ResponseProducer

logger = logging.getLogger(__name__)


class RequestConsumer:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': app_settings.KAFKA_BROKERS,
            'group.id': app_settings.CONSUMER_GROUP_ID,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
        })
        self.running = False

    def start(self, producer: ResponseProducer):
        self.consumer.subscribe([app_settings.REQUEST_TOPIC])
        self.running = True
        logger.info("Started consuming ML requests")

        try:
            while self.running:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())

                if not msg.value():
                    logger.error("RequestConsumer:: Received empty message payload")
                    error = MLError(
                        request_id="unknown",
                        error="Empty message payload received"
                    )
                    producer.send_error(error)
                    continue

                try:
                    # print(msg)
                    request_data = msg.value().decode('utf-8')
                    print(request_data)

                    if not request_data.strip():
                        raise ValueError("Empty JSON payload")

                    request_data = json.loads(request_data)
                    mlrequest = MLRequest(**request_data)
                    print(mlrequest)
                    # request = MLRequest.model_validate(request_data)
                    # logger.info(f"RequestConsumer:: Processing request {request.request_id}")

                    response = process_request(mlrequest)

                    # producer.send_response(response)

                    self.consumer.commit(msg)

                except json.JSONDecodeError as e:
                    logger.error(f"RequestConsumer:: Invalid JSON payload: {e}")
                    error = MLError(
                        request_id="unknown",
                        error=f"Invalid JSON format: {str(e)}"
                    )
                    producer.send_error(error)
                except Exception as e:
                    logger.error(f"RequestConsumer:: Error processing request: {e}")
                    error = MLError(
                        request_id=request.request_id if 'request' in locals() else "unknown",
                        error=str(e)
                    )
                    producer.send_error(error)

        except KeyboardInterrupt:
            self.running = False
        finally:
            self.consumer.close()
