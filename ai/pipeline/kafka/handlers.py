import sys
import base64
import io
import soundfile as sf
import json
import os

from requests import session

sys.path.append('.')
from schemas.messages import MLResponse, MLRequest

from factory.config import FactoryConfig, ENGLISH, HINDI, TELUGU, MARATHI

from pipeline.triage.helpers.v1 import get_follow_up_text_response, _handle_llama_33_70b_call_no_streaming, \
    _get_breakpoints
from pipeline.triage.helpers.v1 import respond_back_in_audio_streaming_followup
from pipeline.helpers.v1 import audio_stream, text_stream, respond_back_in_audio_streaming, get_text_response

from utils.stt.e2e.whisper import get_text
from utils.tts.indic import get_audio_using_tts

IP_PROMPT = """You are a message classification assistant. Your task is to categorize user messages into one of the following three categories based on their content:

1. scheme_info – The user is inquiring about a medical scheme, insurance plan, government healthcare program, or any benefit-related policy.
2. consultation – The user is describing symptoms, asking about an illness, requesting medical advice, or discussing health concerns.
3. greeting – The user is engaging in small talk, saying hello, expressing thanks, or making general friendly conversation without seeking information or help.

Classify each message into only one of the three categories: scheme_info, consultation, or greeting.

Output Format:
Only return the category name in lowercase without any explanation.

Examples:

User: Hi, I hope you're doing well!
Assistant: greeting

User: Can you tell me about the Ayushman Bharat scheme?
Assistant: scheme_info

User: I’ve been having chest pain and shortness of breath for two days.
Assistant: consultation

User: Good morning, doctor!
Assistant: greeting

User: What benefits do I get under the CGHS scheme?
Assistant: scheme_info

User: I have a sore throat and slight fever since last night. Should I be worried?
Assistant: consultation

User: Thanks for your help!
Assistant: greeting

User: How do I apply for the state medical reimbursement program?
Assistant: scheme_info

User: I’m feeling dizzy and lightheaded most of the time.
Assistant: consultation
"""

CHAT_HISTORY_STORAGE = 'chathistory'


def _get_curr_state(session_id):
    if os.path.exists(f'{CHAT_HISTORY_STORAGE}/{session_id}_state.json'):
        with open(f'{CHAT_HISTORY_STORAGE}/{session_id}_state.json', 'r') as handle:
            data = json.load(handle)
        return data.get('curr_state')
    return None


def _update_curr_state(session_id, state):
    try:
        with open(f'{CHAT_HISTORY_STORAGE}/{session_id}_state.json', 'w') as handle:
            json.dump({'curr_state': state}, handle)
        return True
    except:
        return False


GREETING_INTENT = 'greeting'
SCHEME_INTENT = 'scheme_info'
CONSULTATION_INTENT = 'consultation'


def get_intent(session_id, text):
    curr_state = _get_curr_state(session_id)
    if curr_state in [SCHEME_INTENT, CONSULTATION_INTENT]:
        return curr_state
    else:
        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=IP_PROMPT,
            ),
            FactoryConfig.llm.create_message(role="user", content=text),
        ]
        breakpoints = _get_breakpoints(language=ENGLISH)
        response = _handle_llama_33_70b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=ENGLISH)

        if 'greeting' in response:
            intent = GREETING_INTENT
        elif 'scheme_info' in response:
            intent = SCHEME_INTENT
        elif 'consultation' in response:
            intent = CONSULTATION_INTENT

        _update_curr_state(session_id=session_id, state=intent)
        return intent


def get_audio_intent(session_id, audio_path, language):
    text = get_text(audio_path, language=language)

    curr_state = _get_curr_state(session_id)
    if curr_state in [SCHEME_INTENT, CONSULTATION_INTENT]:
        return curr_state
    else:
        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=IP_PROMPT,
            ),
            FactoryConfig.llm.create_message(role="user", content=text),
        ]
        breakpoints = _get_breakpoints(language=ENGLISH)
        response = _handle_llama_33_70b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=ENGLISH)
        if 'greeting' in response:
            intent = GREETING_INTENT
        elif 'scheme_info' in response:
            intent = SCHEME_INTENT
        elif 'consultation' in response:
            intent = CONSULTATION_INTENT

        _update_curr_state(session_id=session_id, state=intent)
        return intent


GREETING_RESPONSES = {
    ENGLISH: "Hey, you can consult about and illness as well as you can know about government medical schemes.",
    HINDI: "आप बीमारी के बारे में परामर्श ले सकते हैं और सरकारी स्वास्थ्य योजनाओं के बारे में भी जान सकते हैं।",
    TELUGU: "అయ్యో, మీరు వ్యాధుల గురించి సలహా పొందవచ్చు మరియు ప్రభుత్వ వైద్య పథకాల గురించి కూడా తెలుసుకోవచ్చు.",
    MARATHI: "तुम्ही आजारांबद्दल सल्ला घेऊ शकता आणि सरकारी आरोग्य योजना देखील जाणून घेऊ शकता."
}


def handle_text(request: MLRequest, producer) -> list:
    intent = get_intent(request.user_id, request.content)
    if intent == GREETING_INTENT:

        chunk_response = MLRequest(
            request_id=request.request_id,
            content=GREETING_RESPONSES.get(request.language),
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

    elif intent == CONSULTATION_INTENT:
        get_follow_up_text_response(request=request, producer=producer)
    elif intent == SCHEME_INTENT:
        get_text_response(request=request, producer=producer)


def handle_audio(request: MLRequest, producer) -> list:
    audio_path = "../tmp/userAudioData/" + request.content
    intent = get_audio_intent(request.user_id, audio_path, request.language)

    if intent == GREETING_INTENT:
        speech = get_audio_using_tts(text=GREETING_RESPONSES.get(request.language), language=request.language)
        chunk_response = MLRequest(
            request_id=request.request_id,
            content=speech,
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

    elif intent == CONSULTATION_INTENT:
        respond_back_in_audio_streaming_followup(request=request, producer=producer)
    elif intent == SCHEME_INTENT:
        respond_back_in_audio_streaming(request=request, producer=producer)
