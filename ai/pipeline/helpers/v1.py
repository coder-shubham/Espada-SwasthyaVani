import sys
import base64
import io
import soundfile as sf
import os

sys.path.append('.')
from schemas.messages import MLResponse, MLRequest

from factory.config import FactoryConfig
from utils.vectorstores.weav8 import WeaviateCollectionClient
from utils.stt.whisper import speech_to_text

from playsound3 import playsound

import soundfile as sf


def _prepare_context(results):
    context = str()

    for i, chunk in enumerate(results):
        context += f'Chunk {i + 1}: {chunk}'
        context += '\n\n'

    return context


def text_stream(audio=None, message=None):
    text = ''
    if audio:
        text = speech_to_text(audio)
    
    if message:
        text = message

    coll_client = WeaviateCollectionClient(db_client=FactoryConfig.vector_db_client, name='gov_schemes',
                                           embeddings=FactoryConfig.embeddings)
    coll_client.load_collection()
    results = coll_client.query(query=text, top_k=2)

    messages = [
        FactoryConfig.llm.create_message(
            role="system",
            content="You are a helpful medical scheme assistant.  You answer concisely. You will be given a query and some context, whatever the language of the query is, respond the answer in that language only. You should not go beyond context, answer strictly from the provided context only.",
        ),
        FactoryConfig.llm.create_message(role="user", content=f"Query: {text}. Context: {_prepare_context(results)}"),
    ]
    curr_chunk = ''
    for chunk in FactoryConfig.llm.stream_response(messages):
        curr_chunk += chunk.message.content
        if any(item in curr_chunk for item in ['\u0970', '\u0964', ',', '.', '?']):
            yield curr_chunk
            curr_chunk = ''
        else:
            pass

    yield curr_chunk

    # def respond_back_in_audio(audio):
    #     for txt_chunk in text_stream(audio):
    #         generator = FactoryConfig.tts_pipeline_hindi(txt_chunk, voice='af_heart')
    #         for i, (gs, ps, audio) in enumerate(generator):
    #             sf.write(f'temp_audio_{i}.wav', audio, 24000)
    #             playsound(f'temp_audio_{i}.wav')
    #             os.remove(f'temp_audio_{i}.wav')


def respond_back_in_audio_streaming(request: MLRequest, producer) -> list:
    audio_path = "../tmp/userAudioData/" + request.content
    collected_chunks = []

    for txt_chunk in text_stream(audio=audio_path):
        generator = FactoryConfig.tts_pipeline_hindi(txt_chunk, voice='af_heart')
    #     for i, (gs, ps, audio) in enumerate(generator):
    #         sf.write(f'temp_audio_{i}.wav', audio, 24000)
    #         playsound(f'temp_audio_{i}.wav')
    #         os.remove(f'temp_audio_{i}.wav')

        for _, _, audio_data in generator:
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, 24000, format='WAV')
            buffer.seek(0)

            audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')

            collected_chunks.append(audio_base64)

            chunk_response = MLRequest(
                request_id=request.request_id,
                content=audio_base64,
                user_id=request.user_id,
                request_type=request.request_type
            )

            producer.send_response(chunk_response)

    return collected_chunks


if __name__ == "__main__":
    for item in text_stream(message="आयुष्मान भारत के बारे में बताइए"):
        print(item)