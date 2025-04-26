from services.producer import ResponseProducer
from services.consumer import RequestConsumer

if __name__ == "__main__":
    producer = ResponseProducer()
    consumer = RequestConsumer()
    consumer.start(producer)
