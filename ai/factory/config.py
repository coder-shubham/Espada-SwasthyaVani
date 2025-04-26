import weaviate
import os
from weaviate.classes.init import Auth
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from dotenv import load_dotenv

load_dotenv()

from utils.llms.ollama.llama import OllamaLlama3Client

from kokoro import KPipeline



def _get_stt_pipe():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )
    return pipe

def _get_vector_db_client():
    weaviate_api_key = os.getenv('WEAVIATE_API_KEY')
    return weaviate.connect_to_local(auth_credentials=Auth.api_key(weaviate_api_key))

def _get_embeddings_instance(model='intfloat/multilingual-e5-large'):
    return SentenceTransformer(model)

def _get_llm_client():
    return OllamaLlama3Client(model_name="llama3.1:8b", temperature=0.0, max_tokens=2048)

class FactoryConfig:
    embeddings = None
    llm = None
    vector_db_client = None
    stt_pipe = None


FactoryConfig.vector_db_client = _get_vector_db_client()
FactoryConfig.embeddings = _get_embeddings_instance()
FactoryConfig.llm = _get_llm_client()
FactoryConfig.stt_pipe = _get_stt_pipe()
FactoryConfig.tts_pipeline_hindi = KPipeline(lang_code='h')
