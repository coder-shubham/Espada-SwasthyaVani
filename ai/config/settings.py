import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KAFKA_BROKERS: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    REQUEST_TOPIC: str = os.getenv("REQUEST_TOPIC", "ml-topic")
    RESPONSE_TOPIC: str = os.getenv("RESPONSE_TOPIC", "backend-topic")
    CONSUMER_GROUP_ID: str = os.getenv("CONSUMER_GROUP_ID", "ml-service-group")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "")
    LLAMA_33_70B_API_KEY: str = os.getenv("LLAMA_33_70B_API_KEY", "")
    LLAMA_33_70B_BASE_URL: str = os.getenv("LLAMA_33_70B_BASE_URL", "")
    PRODUCTION: str = os.getenv("PRODUCTION", "")
    INDIC_TTS_BASE_URL: str = os.getenv("INDIC_TTS_BASE_URL", "")
    E2E_TIR_ACCESS_TOKEN: str = os.getenv("E2E_TIR_ACCESS_TOKEN", "")
    E2E_TIR_API_KEY: str = os.getenv("E2E_TIR_API_KEY", "")
    E2E_TIR_PROJECT_ID: str = os.getenv("E2E_TIR_PROJECT_ID", "")
    E2E_TIR_TEAM_ID: str = os.getenv("E2E_TIR_TEAM_ID", "")
    LLAMA_31_405B_BASE_URL: str = os.getenv("LLAMA_31_405B_BASE_URL", "")

    class Config:
        env_file = ".env"


app_settings = Settings()
