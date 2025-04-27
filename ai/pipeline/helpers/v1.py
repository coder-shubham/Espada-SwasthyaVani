import sys
import base64
import io
import soundfile as sf
import os

sys.path.append('.')
from schemas.messages import MLResponse, MLRequest

from factory.config import FactoryConfig
from factory.constants import ENGLISH, HINDI, LLAMA_33_70B_ID
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

def _get_breakpoints(language=ENGLISH):
    if language == ENGLISH:
        return [',', '.', '?', '!']
    elif language == HINDI:
        return ['\u0970', '\u0964', ',', '.', '?']


def _handle_local_llama_31_8b_call(messages, breakpoints, language=ENGLISH):
    curr_chunk = str()
    for i, chunk in enumerate(FactoryConfig.llm.stream_response(messages)):
        curr_chunk += chunk.message.content
        if any(item in curr_chunk for item in breakpoints):
            curr_chunk = curr_chunk.replace('*', '')
            if i == 0:
                first_chunk = curr_chunk
            elif i == 1:
                yield first_chunk
                yield curr_chunk
            else:
                yield curr_chunk
            curr_chunk = str()
        else:
            pass

    yield curr_chunk


def _handle_llama_33_70b_call(messages, breakpoints, language=ENGLISH):
    completion = FactoryConfig.llama_33_70b_client.chat.completions.create(
        model=LLAMA_33_70B_ID,
        messages=messages,
        temperature=0.0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.1,
        presence_penalty=1,
        stream=True
    )
    curr_chunk = str()
    for i, chunk in enumerate(completion):
        if chunk.choices and chunk.choices[0].delta.content is not None:
            curr_chunk += chunk.choices[0].delta.content
            
            if any(item in curr_chunk for item in breakpoints):
                curr_chunk = curr_chunk.replace('*', '')
                
                if i == 0:
                    first_chunk = curr_chunk
                elif i == 1:
                    yield first_chunk
                    yield curr_chunk
                else:
                    yield curr_chunk
                curr_chunk = str()
    
    yield curr_chunk


def text_stream(audio=None, message=None, language=ENGLISH):
    text = str()
    if audio:
        text = speech_to_text(audio, language=language)
        print("Speech to Text Output: ", text)

    if message:
        text = message

    coll_client = WeaviateCollectionClient(db_client=FactoryConfig.vector_db_client, name='gov_schemes',
            embeddings=FactoryConfig.embeddings)
    coll_client.load_collection()
    results = coll_client.query(query=text, top_k=5)
    
    messages = [
        FactoryConfig.llm.create_message(
            role="system",
            content=f"You are a helpful medical scheme assistant. You answer concisely in {FactoryConfig.language_name[language]} language only. You will be given a query and some context, whatever the language of the query is, respond the answer in {FactoryConfig.language_name[language]} language only. You should not go beyond context, answer strictly from the provided context only.",
        ),
        FactoryConfig.llm.create_message(role="user", content=f"Query: {text}. Context: {_prepare_context(results)}. Respond in {FactoryConfig.language_name[language]} language only"),
    ]
    
    breakpoints = _get_breakpoints(language)
    
    if FactoryConfig.production:
        for txt_chunk in _handle_llama_33_70b_call(messages=messages, breakpoints=breakpoints, language=language):
            yield txt_chunk
    else:
        for txt_chunk in _handle_local_llama_31_8b_call(messages=messages, breakpoints=breakpoints, language=language):
            yield txt_chunk

    # def respond_back_in_audio(audio):
    #     for txt_chunk in text_stream(audio):
    #         generator = FactoryConfig.tts_pipeline_hindi(txt_chunk, voice='af_heart')
    #         for i, (gs, ps, audio) in enumerate(generator):
    #             sf.write(f'temp_audio_{i}.wav', audio, 24000)
    #             playsound(f'temp_audio_{i}.wav')
    #             os.remove(f'temp_audio_{i}.wav')



def audio_stream(audio_path, language=ENGLISH):
    for txt_chunk in text_stream(audio=audio_path, language=language):
        generator = FactoryConfig.tts_model[language](txt_chunk, voice='af_heart')
        # for i, (gs, ps, audio) in enumerate(generator):
        #     sf.write(f'temp_audio_{i}.wav', audio, 24000)
        #     playsound(f'temp_audio_{i}.wav')
        #     os.remove(f'temp_audio_{i}.wav')
        for _, _, audio_data in generator:
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, 24000, format='WAV')
            buffer.seek(0)
            audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            yield audio_base64



def respond_back_in_audio_streaming(request: MLRequest, producer) -> list:
    audio_path = "../tmp/userAudioData/" + request.content
    
    for base_64_chunk in audio_stream(audio_path=audio_path, language=request.language):
        chunk_response = MLRequest(
            request_id=request.request_id,
            content=base_64_chunk,
            user_id=request.user_id,
            request_type=request.request_type,
            timestamp=request.timestamp,
            timestampInLong=request.timestampInLong,
            sender=request.sender,
            language=request.language,
            type=request.type
        )
        producer.send_response(chunk_response)


def get_text_response(request: MLRequest, producer) -> list:
    message = request.content

    for ml_response in text_stream(message=message, language=request.language):
        chunk_response = MLRequest(
            request_id=request.request_id,
            content=ml_response,
            user_id=request.user_id,
            request_type=request.request_type,
            timestamp=request.timestamp,
            timestampInLong=request.timestampInLong,
            sender=request.sender,
            language=request.language,
            type=request.type
        )

        producer.send_response(chunk_response)


if __name__ == "__main__":
    for item in text_stream(message="आयुष्मान भारत के बारे में बताइए", language=HINDI):
        print(item)
    
    # audio_stream(audio_path='testaudio.mp3', language=HINDI)
