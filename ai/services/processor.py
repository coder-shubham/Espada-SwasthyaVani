import logging
from schemas.messages import MLRequest, MLResponse

from pipeline.kafka.handlers import handle_audio, handle_text

logger = logging.getLogger(__name__)


def process_request(request: MLRequest, producer) -> MLResponse:
    try:
        logger.info(f"Processor:: Processing {request.request_type} request with model {request.model}")

        request_type = request.request_type

        if request_type == "audio":
            handle_audio(request, producer)

        elif request_type == "text":
            handle_text(request, producer)

        else:
            raise ValueError(f"Processor:: Unknown type: {request_type}")

    except Exception as e:
        logger.error(f"Processor:: Processing failed: {e}")
        raise


def process_text_classification(request: MLRequest) -> dict:
    """Example text processing function"""
    return {
        "classification": "positive",
        "confidence": 0.95,
        "processed_text": request.content
    }


def process_audio_transcription(request: MLRequest) -> dict:
    """Example audio processing function"""
    return {
        "transcription": "sample transcribed text",
        "confidence": 0.85,
        "audio_length": 5.2
    }
