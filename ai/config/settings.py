import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KAFKA_BROKERS: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    REQUEST_TOPIC: str = os.getenv("REQUEST_TOPIC", "ml-topic")
    RESPONSE_TOPIC: str = os.getenv("RESPONSE_TOPIC", "backend-topic")
    CONSUMER_GROUP_ID: str = os.getenv("CONSUMER_GROUP_ID", "ml-service-group")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "")

    class Config:
        env_file = ".env"


app_settings = Settings()
