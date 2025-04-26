import sys
import base64
import io
import soundfile as sf
import os

from schemas.messages import MLResponse, MLRequest

sys.path.append('.')

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


def text_stream(audio):
    text = speech_to_text(audio)

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
    audio_path = request.content
    collected_chunks = []

    with open(audio_path, 'rb') as f:
        audio_file_data = f.read()

    for txt_chunk in text_stream(audio_file_data):
        generator = FactoryConfig.tts_pipeline_hindi(txt_chunk, voice='af_heart')
        for i, (gs, ps, audio) in enumerate(generator):
            sf.write(f'temp_audio_{i}.wav', audio, 24000)
            playsound(f'temp_audio_{i}.wav')
            os.remove(f'temp_audio_{i}.wav')

        for _, _, audio_data in generator:
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, 24000, format='WAV')
            buffer.seek(0)

            audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')

            collected_chunks.append(audio_base64)

            chunk_response = MLResponse(
                request_id=request.request_id,
                result={
                    "audio_base64": audio_base64
                },
                model=request.model
            )

            producer.send_response(chunk_response)

    return collected_chunks


if __name__ == '__main__':
# respond_back_in_audio('testaudio.mp3')
