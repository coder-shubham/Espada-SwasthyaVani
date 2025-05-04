import weaviate
import os
from openai import OpenAI
from weaviate.classes.init import Auth
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from e2enetworks.cloud import tir

from dotenv import load_dotenv

load_dotenv()

from utils.llms.ollama.llama import OllamaLlama3Client
from factory.constants import KOKORO_ENGLISH_CODE, KOKORO_HINDI_CODE, KOKORO_REPO_ID
from factory.constants import WHISPER_ENGLISH_CODE, WHISPER_HINDI_CODE
from factory.constants import HINDI, ENGLISH, MARATHI, TELUGU

from factory.constants import WHISPER_LARGE_V3_MODEL_ID, WHISPER_PIPELINE
from factory.constants import MULTILINGUAL_E5_MODEL_ID, LLAMA_31_8B_ID

from factory.constants import CREDITS_CAN_BE_CONSUMED_NOW

from kokoro import KPipeline



def _get_stt_pipe():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = WHISPER_LARGE_V3_MODEL_ID

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        WHISPER_PIPELINE,
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

class FactoryConfig:
    embeddings = None
    llm = None
    vector_db_client = None
    stt_pipe = None
    tts_pipeline_hindi = None
    tts_pipeline_english = None
    tts_model = dict()
    whisper_lang_code = dict()
    language_name = dict()
    production = False
    llama_33_70b_client = None
    llama_31_405b_client = None
    indic_tts_url = None
    indic_tts_token = None
    tir_client = None


FactoryConfig.vector_db_client = _get_vector_db_client()
FactoryConfig.embeddings = SentenceTransformer(MULTILINGUAL_E5_MODEL_ID)
FactoryConfig.llm = OllamaLlama3Client(model_name=LLAMA_31_8B_ID, temperature=0.0, max_tokens=2048)
FactoryConfig.stt_pipe = _get_stt_pipe()
FactoryConfig.tts_pipeline_english = KPipeline(repo_id=KOKORO_REPO_ID, lang_code=KOKORO_ENGLISH_CODE)
FactoryConfig.tts_pipeline_hindi = KPipeline(repo_id=KOKORO_REPO_ID, lang_code=KOKORO_HINDI_CODE)

if os.getenv('E2E_TIR_ACCESS_TOKEN') and os.getenv('E2E_TIR_API_KEY') and os.getenv('E2E_TIR_PROJECT_ID') and os.getenv('E2E_TIR_TEAM_ID'):
    tir.init()
    FactoryConfig.tir_client = tir.ModelAPIClient()

if os.getenv('LLAMA_33_70B_BASE_URL') and os.getenv('LLAMA_33_70B_API_KEY') and os.getenv('PRODUCTION') and os.getenv('PRODUCTION').lower() == CREDITS_CAN_BE_CONSUMED_NOW.lower():
    FactoryConfig.llama_33_70b_client = OpenAI(base_url=os.getenv('LLAMA_33_70B_BASE_URL')
                                        ,api_key=os.getenv('LLAMA_33_70B_API_KEY'))
    FactoryConfig.production = True

if FactoryConfig.production and os.getenv('LLAMA_31_405B_BASE_URL'):
    FactoryConfig.llama_31_405b_client = OpenAI(
        base_url=os.getenv('LLAMA_31_405B_BASE_URL'), api_key=os.getenv('LLAMA_33_70B_API_KEY') # as same api key will work
    )

# Telugu & Marathi pending for now, as no tts model integrated for these two.

FactoryConfig.tts_model[ENGLISH] = FactoryConfig.tts_pipeline_english
FactoryConfig.tts_model[HINDI] = FactoryConfig.tts_pipeline_hindi

FactoryConfig.whisper_lang_code[ENGLISH] = WHISPER_ENGLISH_CODE
FactoryConfig.whisper_lang_code[HINDI] = WHISPER_HINDI_CODE

FactoryConfig.language_name[ENGLISH] = 'English'
FactoryConfig.language_name[HINDI] = 'Hindi'
FactoryConfig.language_name[MARATHI] = 'Marathi'
FactoryConfig.language_name[TELUGU] = 'Telugu'
FactoryConfig.indic_tts_url = os.getenv('INDIC_TTS_BASE_URL')
FactoryConfig.indic_tts_token = os.getenv('LLAMA_33_70B_API_KEY')

