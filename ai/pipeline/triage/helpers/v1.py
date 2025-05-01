import sys
import base64
import io
import soundfile as sf
import json
import os

from schemas.messages import MLRequest

sys.path.append('.')

from factory.config import FactoryConfig
from factory.constants import HINDI, ENGLISH
from utils.stt.whisper import speech_to_text
from pipeline.triage.prompts.v1 import SYSTEM_PROMPT_FOLLOWUP, SPECIALIZATION_FILTER_PROMPT
from pipeline.helpers.v1 import _get_breakpoints, _handle_llama_33_70b_call, _handle_local_llama_31_8b_call, _handle_llama_33_70b_call_no_streaming
from utils.vectorstores.weav8 import WeaviateCollectionClient
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
        return followup
    
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
        return {
            "specializations": filter_json.get('specializations')
        }




def get_follow_up_text_response(request: MLRequest, producer) -> list:
    message = request.content
    session_id = request.user_id
    language = request.language

    response = text_stream_followup(session_id=session_id, message=message, language=language)

    print("get_follow_up_text_response:: response: ", response)
    if isinstance(response, dict):
        response = response.get("specializations")

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

if __name__ == '__main__':
    pass
    result = text_stream_followup(session_id='abctest', message='thanks you', language=ENGLISH)
    print(result)
    