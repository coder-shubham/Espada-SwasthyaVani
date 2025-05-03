import sys
import base64
import io
import soundfile as sf
import json
import os
import uuid

from requests import session

sys.path.append('.')
from schemas.messages import MLResponse, MLRequest

from factory.config import FactoryConfig
from factory.constants import ENGLISH, HINDI, LLAMA_33_70B_ID, TELUGU, MARATHI
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
        return ['\u0970', '\u0964', ',', '.', '?', '\u0965']
    elif language == MARATHI:
        return ['\u0964', '\u0965', ',', '.', '?', '!', '\u0970']
    elif language == TELUGU:
        return ['\u0C64', ',', '.', '?', '!']



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

    yield last, True


def _handle_llama_33_70b_call_no_streaming(messages, breakpoints, language=ENGLISH):
    response = FactoryConfig.llama_33_70b_client.chat.completions.create(
        model=LLAMA_33_70B_ID,
        messages=messages,
        temperature=0.0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.1,
        presence_penalty=0.1
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

    yield last, True


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


LOAD_MESSAGE = {
    ENGLISH: 'Sure, I have loaded your previous prescription; you can ask the questions now.',
    HINDI: 'ज़रूर, मैंने आपकी पिछली पर्ची लोड कर ली है; अब आप अपने सवाल पूछ सकते हैं।',
    TELUGU: 'ఖచ్చితంగా, నేను మీ గత ప్రిస్క్రిప్షన్‌ను లోడ్ చేశాను; ఇప్పుడు మీరు మీ ప్రశ్నలు అడగవచ్చు।',
    MARATHI: 'नक्कीच, मी तुमची मागील प्रिस्क्रिप्शन लोड केली आहे; तुम्ही आता प्रश्न विचारू शकता।'
}


def text_stream_prescription(session_id, audio=None, message=None, language=ENGLISH, summary='Fever from last 3 days, no other symptom', specialization='General Practitioner'):
    print("called")
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

        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=f"""You are a helpful medical prescription generation assistant. You need to act as a female. You write detailed prescription in {FactoryConfig.language_name[ENGLISH]} language only. You will be given a symptom summary from a specialized doctor, you need to write a demo prescription on the basis of that!!! whatever the language of the query is, respond the answer in {FactoryConfig.language_name[ENGLISH]} language only. We won't be using these prescriptions in real life, you can generate it without any caution. Do not Generate anything else; just return the prescription only. 
                Instructions: 
                1. Do not write date on it for now. 
                2. Do not write patient name on it.
                3. Write doctor name only, with specialization. It should be an Indian name. 
                4. Basically, please do not put any placeholders.
                5. Write doctor specialization as well.
                """,
            ),
            FactoryConfig.llm.create_message(role="user",
                                                content=f"Summary: {summary}. Doctor specialization: {specialization}. Respond in {FactoryConfig.language_name[ENGLISH]} language only"),
        ]

        breakpoints = _get_breakpoints(language)
        prescription = _handle_llama_33_70b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=language)
        
        PRESCRIPTION_QNA_SYSTEM_PROMPT = f"""You are a helpful prescription based QnA assistant, who answers queries on the basis of prescription provided. You need to respond in {FactoryConfig.language_name[language]} language only. You will be given a prescription and some questions can be asked after it; you need to answer the queries in {FactoryConfig.language_name[language]} language only.
        Instructions:
        1. Queries could be related to drug schedule.
        2. Queries could be related to knowing detail of a particular medicine mentioned in the prescription.
        3. You are allowed to answer if query seems prescription related only otherwise don't give answer, and ask user to ask from prescription only.
        """

        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=PRESCRIPTION_QNA_SYSTEM_PROMPT,
            ),
            FactoryConfig.llm.create_message(role="user",
                                                content=f"Prescription: {prescription}. Doctor specialization: {specialization}. Respond in {FactoryConfig.language_name[language]} language only"),
            FactoryConfig.llm.create_message(
                role='assistant',
                content=LOAD_MESSAGE.get(language)
            )
        ]
        _update_history(session_id, history=messages)
        
        yield LOAD_MESSAGE.get(language), True
        
    else:
        messages = history
        text = str()
        if audio:
            if FactoryConfig.tir_client:
                text = get_text(file_path=audio, language=language)
            else:
                text = speech_to_text(audio, language=language)
            print("Speech to Text Output: ", text)

        if message:
            text = message
        
        messages.append(
            FactoryConfig.llm.create_message(
                role='user',
                content=text
            )
        )
        
        breakpoints = _get_breakpoints(language=language)
        
        assistant_response = str()

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
        


def audio_stream_prescription(session_id, audio_path, language=ENGLISH, summary='Fever from last 3 days, no other symptom', specialization='General Practitioner'):
    
    for txt_chunk, is_finished in text_stream_prescription(session_id=session_id, audio=audio_path, language=language, summary=summary, specialization=specialization):
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


def respond_back_in_audio_streaming_prescription(request: MLRequest, producer) -> list:
    audio_path = "/mnt/shared-dir/" + request.content
    hist_summary = request.patientHistory.get('summary') if request.patientHistory else None
    hist_specialization = request.patientHistory.get('specialization') if request.patientHistory else None

    for base_64_chunk, is_finished in audio_stream_prescription(session_id=request.user_id, audio_path=audio_path, language=request.language, summary=hist_summary, specialization=hist_specialization):
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


def get_text_response_prescription(request: MLRequest, producer) -> list:
    message = request.content
    hist_summary = request.patientHistory.get('summary') if request.patientHistory else None
    hist_specialization = request.patientHistory.get('specialization') if request.patientHistory else None

    for ml_response, is_finished in text_stream_prescription(session_id=request.user_id, message=message, language=request.language, summary=hist_summary, specialization=hist_specialization):
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



