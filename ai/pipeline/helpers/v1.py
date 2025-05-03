import sys
import base64
import io
import soundfile as sf
import json
import os

from requests import session

sys.path.append('.')
from schemas.messages import MLResponse, MLRequest

from factory.config import FactoryConfig
from factory.constants import ENGLISH, HINDI, LLAMA_33_70B_ID
from utils.vectorstores.weav8 import WeaviateCollectionClient
from utils.stt.whisper import speech_to_text
from utils.stt.e2e.whisper import get_text
from utils.tts.indic import get_audio_using_tts

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
    iterable = FactoryConfig.llm.stream_response(messages)
    last = None

    for chunk in iterable:
        curr_chunk += chunk.message.content
        if any(item in curr_chunk for item in breakpoints):
            curr_chunk = curr_chunk.replace('*', '')
            if not last:
                pass
            else:
                yield last, False
            last = curr_chunk
            curr_chunk = str()

    yield curr_chunk, True


def _handle_llama_33_70b_call_no_streaming(messages, breakpoints, language=ENGLISH):
    response = FactoryConfig.llama_33_70b_client.chat.completions.create(
        model=LLAMA_33_70B_ID,
        messages=messages,
        temperature=0.0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.05,
        presence_penalty=0.05
    )
    return response.choices[0].message.content if response.choices and response.choices[0].message else {}


def _handle_llama_33_70b_call(messages, breakpoints, language=ENGLISH):
    curr_chunk = str()
    iterable = FactoryConfig.llama_33_70b_client.chat.completions.create(
        model=LLAMA_33_70B_ID,
        messages=messages,
        temperature=0.0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.1,
        presence_penalty=1,
        stream=True
    )
    last = None

    for chunk in iterable:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            curr_chunk += chunk.choices[0].delta.content

            if any(item in curr_chunk for item in breakpoints):
                curr_chunk = curr_chunk.replace('*', '')
                if not last:
                    pass
                else:
                    yield last, False
                last = curr_chunk
                curr_chunk = str()

    yield curr_chunk, True


CHAT_HISTORY_STORAGE = 'chathistory'

def _get_session_history(session_id):
    if os.path.exists(f'{CHAT_HISTORY_STORAGE}/{session_id}.json'):
        with open(f'{CHAT_HISTORY_STORAGE}/{session_id}.json', 'r') as handle:
            data = json.load(handle)
        return data
    return None

def _update_history(session_id, history):
    try:
        with open(f'{CHAT_HISTORY_STORAGE}/{session_id}.json', 'w') as handle:
            json.dump(history, handle)
        return True
    except:
        return False


def text_stream(session_id, audio=None, message=None, language=ENGLISH):
    
    history = _get_session_history(session_id=session_id)
    
    if not history:
        text = str()
        if audio:
            if FactoryConfig.tir_client:
                text = get_text(file_path=audio, language=language)
            else:
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
                content=f"You are a helpful medical scheme female assistant. You answer concisely in {FactoryConfig.language_name[language]} language only. You will be given a query and some context, whatever the language of the query is, respond the answer in {FactoryConfig.language_name[language]} language only. You should not go beyond context, answer strictly from the provided context only.",
            ),
            FactoryConfig.llm.create_message(role="user",
                                                content=f"Query: {text}. Context: {_prepare_context(results)}. Respond in {FactoryConfig.language_name[language]} language only"),
        ]

        breakpoints = _get_breakpoints(language)
        
        assistant_response = str()
        txt_chunk, is_finished = None, None

        if FactoryConfig.production:
            for txt_chunk, is_finished in _handle_llama_33_70b_call(messages=messages, breakpoints=breakpoints,
                                                                    language=language):
                assistant_response += txt_chunk
                if is_finished:
                    messages.pop()
                    messages.append(
                        FactoryConfig.llm.create_message(role="user",
                        content=text)
                    )
                    messages.append(
                        FactoryConfig.llm.create_message(role="assistant",
                        content=assistant_response)
                    )
                    _update_history(session_id, history=messages)
                
                yield txt_chunk, is_finished
        else:
            for txt_chunk, is_finished in _handle_local_llama_31_8b_call(messages=messages, breakpoints=breakpoints,
                                                                            language=language):
                assistant_response += txt_chunk
                if is_finished:
                    messages.pop()
                    messages.append(
                        FactoryConfig.llm.create_message(role="user",
                        content=text)
                    )
                    messages.append(
                        FactoryConfig.llm.create_message(role="assistant",
                        content=assistant_response)
                    )
                    _update_history(session_id, history=messages)
                
                yield txt_chunk, is_finished
    else:
        text = str()
        if audio:
            if FactoryConfig.tir_client:
                text = get_text(file_path=audio, language=language)
            else:
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
                content=f"""You are a helpful query analysis assistant. You return contextualized query in {FactoryConfig.language_name[language]} language only. You will be given a query and some history, whatever the language of the query is, respond the contextualized query in {FactoryConfig.language_name[language]} language only. You should respond with any other detail, return the contextualized query only.
                Instructions: Either the query is standalone, can be understood without referencing previous previous messages, return it as it is in `contextualized_query` field.
                Otherwise it would be related to previous queries, in that case return a contextualized query.
                Response format: ```json{{"contextualized_query": "<contextualized query here>"}}""",
            ),
            FactoryConfig.llm.create_message(role="user",
                                                content=f"Latest query: {text}. Respond in {FactoryConfig.language_name[language]} language only"),
        ]
        
        breakpoints = _get_breakpoints(language)
        response = _handle_llama_33_70b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=language)
        l_index = response.find('{')
        r_index = response.rfind('}')
        try:
            response_json = json.loads(response[l_index:r_index+1])
        except:
            response_json = {}
        
        contextualized_query = response_json.get('contextualized_query')
        
        print(contextualized_query, "contextualized_qery")
        
        
        
        if contextualized_query:
            text = contextualized_query
        else:
            text = message

        coll_client = WeaviateCollectionClient(db_client=FactoryConfig.vector_db_client, name='gov_schemes',
                                                embeddings=FactoryConfig.embeddings)
        coll_client.load_collection()
        results = coll_client.query(query=text, top_k=5)

        
        assistant_response = str()
        txt_chunk, is_finished = None, None
        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=f"You are a helpful medical scheme female assistant. You answer concisely in {FactoryConfig.language_name[language]} language only. You will be given a query and some context, whatever the language of the query is, respond the answer in {FactoryConfig.language_name[language]} language only. If the query is not related to the context, respond in conversational medical agent manner, If query is related to context then use the context to answer the query.",
            ),
            FactoryConfig.llm.create_message(role="user",
                                                content=f"Query: {text}. ** Context (provided by external tool, not provided by the user): {_prepare_context(results)} **. Respond in {FactoryConfig.language_name[language]} language only"),
        ]

        if FactoryConfig.production:
            for txt_chunk, is_finished in _handle_llama_33_70b_call(messages=messages, breakpoints=breakpoints,
                                                                    language=language):
                assistant_response += txt_chunk
                if is_finished:
                    history.append({
                        'role': 'user',
                        'content': text
                    })
                    history.append(
                        {
                        'role': 'assistant',
                        'content': assistant_response
                        }
                    )
                    _update_history(session_id, history=history)
                
                yield txt_chunk, is_finished
                
        else:
            for txt_chunk, is_finished in _handle_local_llama_31_8b_call(messages=messages, breakpoints=breakpoints,
                                                                            language=language):
                assistant_response += txt_chunk
                if is_finished:
                    history.append({
                        'role': 'user',
                        'content': text
                    })
                    history.append(
                        {
                        'role': 'assistant',
                        'content': assistant_response
                        }
                    )
                    _update_history(session_id, history=history)
                
                yield txt_chunk, is_finished
        


def audio_stream(session_id, audio_path, language=ENGLISH):
    
    for txt_chunk, is_finished in text_stream(session_id=session_id, audio=audio_path, language=language):
        if FactoryConfig.indic_tts_url:
            audio_base64 = get_audio_using_tts(txt_chunk, language=language)
            yield audio_base64, is_finished
        else:
            generator = FactoryConfig.tts_model[language](txt_chunk, voice='af_heart')
            # for i, (gs, ps, audio) in enumerate(generator):
            #     sf.write(f'temp_audio_{i}.wav', audio, 24000)
            #     playsound(f'temp_audio_{i}.wav')
            #     os.remove(f'temp_audio_{i}.wav')
            #     print(is_finished)
            for _, _, audio_data in generator:
                buffer = io.BytesIO()
                sf.write(buffer, audio_data, 24000, format='WAV')
                buffer.seek(0)
                audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                yield audio_base64, is_finished


def respond_back_in_audio_streaming(request: MLRequest, producer) -> list:
    audio_path = "../tmp/userAudioData/" + request.content

    for base_64_chunk, is_finished in audio_stream(session_id=request.user_id, audio_path=audio_path, language=request.language):
        chunk_response = MLRequest(
            request_id=request.request_id,
            content=base_64_chunk,
            user_id=request.user_id,
            request_type=request.request_type,
            timestamp=request.timestamp,
            timestampInLong=request.timestampInLong,
            sender=request.sender,
            language=request.language,
            type=request.type,
            isFinished=is_finished
        )
        producer.send_response(chunk_response)


def get_text_response(request: MLRequest, producer) -> list:
    message = request.content

    for ml_response, is_finished in text_stream(session_id=request.user_id, message=message, language=request.language):
        chunk_response = MLRequest(
            request_id=request.request_id,
            content=ml_response,
            user_id=request.user_id,
            request_type=request.request_type,
            timestamp=request.timestamp,
            timestampInLong=request.timestampInLong,
            sender=request.sender,
            language=request.language,
            type=request.type,
            isFinished=is_finished
        )

        producer.send_response(chunk_response)
