import sys
import base64
import io
import soundfile as sf
import json
import os

sys.path.append('.')
from schemas.messages import MLRequest
from playsound3 import playsound


from factory.config import FactoryConfig
from factory.constants import HINDI, ENGLISH
from utils.stt.whisper import speech_to_text
from utils.stt.e2e.whisper import get_text
from pipeline.triage.prompts.v1 import SYSTEM_PROMPT_FOLLOWUP, SPECIALIZATION_FILTER_PROMPT
from pipeline.helpers.v1 import _get_breakpoints, _handle_llama_33_70b_call, _handle_local_llama_31_8b_call, _handle_llama_33_70b_call_no_streaming
from utils.vectorstores.weav8 import WeaviateCollectionClient
from utils.tts.indic import get_audio_using_tts
from collections import Counter

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

def text_stream_followup(session_id, audio=None, message=None, language=ENGLISH):
    
    history = _get_session_history(session_id=session_id)
    
    text = str()
    if audio:
        if FactoryConfig.tir_client:
            text = get_text(file_path=audio, language=language)
        else:
            text = speech_to_text(audio, language=language)
        print("Speech to Text Output: ", text)
    
    if message:
        text = message
    
    if not history:
        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=SYSTEM_PROMPT_FOLLOWUP.format(language=FactoryConfig.language_name[language]),
            ),
            FactoryConfig.llm.create_message(role="user", content=f"Query: {text}. Respond in {FactoryConfig.language_name[language]} language only"),
        ]
    
    else:
        messages = history
        messages.append(FactoryConfig.llm.create_message(role="user", content=f"Query: {text}. Respond in {FactoryConfig.language_name[language]} language only"))
    
    breakpoints = _get_breakpoints(language)
    
    if FactoryConfig.production:
        result = _handle_llama_33_70b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=language)
        
    
    l_index = result.find('{')
    r_index = result.rfind('}')
    try:
        raw_json = json.loads(result[l_index:r_index+1])
        
        followup = raw_json.get('followup').strip()
        contextualized_query = raw_json.get('contextualized_query')
    except:
        followup = ''
        contextualized_query = ''
    
    if followup:
        messages.append({
            'role': 'assistant',
            'content': followup
        })
        _update_history(session_id=session_id, history=messages)
        return {
            'specialization': None,
            'response': followup
        }
    
    elif contextualized_query:
        
        # coll_client = WeaviateCollectionClient(db_client=FactoryConfig.vector_db_client, name='specialization',
        #         embeddings=FactoryConfig.embeddings)
        # coll_client.load_collection()
        # chunks_retrieved = coll_client.query(query=text, top_k=20)
        
        # # with open('results.json', 'w') as handle:
        # #     json.dump(chunks_retrieved, handle)
        
        
        # specializations = list()
        # for cr in chunks_retrieved:
        #     properties = cr.get('properties')
        #     specialization = properties.get('specialization')
        #     if specialization not in specializations and len(specializations) < 6:
        #         specializations.append(specialization)
                
        
        symptoms = contextualized_query
        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=SPECIALIZATION_FILTER_PROMPT,
            ),
            FactoryConfig.llm.create_message(role="user", content=f"Symptoms: {symptoms}"),
        ]
        
        filter_result = _handle_llama_33_70b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=language)
        
        l_index = filter_result.find('{')
        r_index = filter_result.rfind('}')
        
        raw_json = filter_result[l_index: r_index+1]
        
        filter_json = json.loads(raw_json)
        print("filter_json: ", filter_json)
        return {
            "specialization": filter_json.get('specialization'),
            "response": filter_json.get('response')
        }


def audio_followup(session_id, audio_path, language=ENGLISH):
    
    result =  text_stream_followup(session_id=session_id, audio=audio_path, language=language)
    if FactoryConfig.indic_tts_url:
        audio_base64 = get_audio_using_tts(result.get('response'), language=language)
        return {'response': None, 'audio_base_64_response': audio_base64, 'specialization': result.get('specialization'), 'isFinished': True }
    else:
    
        generator = FactoryConfig.tts_model[language](result.get('response'), voice='af_heart')
        specialization = result.get('specialization')
        is_finished = True
        # for i, (gs, ps, audio) in enumerate(generator):
        #     print("hello", i)
        #     sf.write(f'temp_audio_{i}.wav', audio, 24000)
        #     playsound(f'temp_audio_{i}.wav')
        #     os.remove(f'temp_audio_{i}.wav')
        #     print(is_finished)
        for _, _, audio_data in generator:
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, 24000, format='WAV')
            buffer.seek(0)
            audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            return {'response': None, 'audio_base_64_response': audio_base64, 'specialization': specialization, 'isFinished': True } # as one time only



def respond_back_in_audio_streaming_followup(request: MLRequest, producer) -> list:
    audio_path = "../tmp/userAudioData/" + request.content
    for result in audio_followup(session_id=request.user_id, audio_path=audio_path, language=request.language):
        print("result: ", result)
        chunk_response = MLRequest(
            request_id=request.request_id,
            content=result.get('audio_base_64_response'),
            user_id=request.user_id,
            request_type=request.request_type,
            timestamp=request.timestamp,
            timestampInLong=request.timestampInLong,
            sender=request.sender,
            language=request.language,
            type=request.type,
            isFinished=result.get('isFinished')
        )
        producer.send_response(chunk_response)

def get_follow_up_text_response(request: MLRequest, producer) -> list:
    message = request.content
    session_id = request.user_id
    language = request.language

    response = text_stream_followup(session_id=session_id, message=message, language=language)

    print("Response: ", response)
    if isinstance(response, dict):
        response = response.get("response")

    chunk_response = MLRequest(
        request_id=request.request_id,
        content=response,
        user_id=request.user_id,
        request_type=request.request_type,
        timestamp=request.timestamp,
        timestampInLong=request.timestampInLong,
        sender=request.sender,
        language=request.language,
        type=request.type,
        isFinished=True
    )

    producer.send_response(chunk_response)