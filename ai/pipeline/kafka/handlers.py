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
from pipeline.triage.helpers.v1 import respond_back_in_audio_streaming_followup, audio_followup, text_stream_followup
from pipeline.helpers.v1 import audio_stream, text_stream, respond_back_in_audio_streaming, get_text_response, _handle_llama_31_405b_call_no_streaming, _handle_llama_31_405b_call
from pipeline.prescription.helpers.v1 import respond_back_in_audio_streaming_prescription, get_text_response_prescription

from utils.stt.e2e.whisper import get_text
from utils.tts.indic import get_audio_using_tts

IP_PROMPT = """You are a message classification assistant. Your task is to categorize user messages into one of the following three categories based on their content:

1. scheme_info – The user is inquiring about a medical scheme, insurance plan, government healthcare program, or any benefit-related policy.
2. consultation – The user is describing symptoms, asking about an illness, requesting medical advice, or discussing health concerns.
3. prescription - The user is trying to understand medicines and schedules from last prescription.
3. greeting – The user is engaging in small talk, saying hello, expressing thanks, or making general friendly conversation without seeking information or help.

Classify each message into only one of the three categories: scheme_info, consultation, or greeting.

Output Format:
Only return the category name in lowercase without any explanation.

Examples:

User: Hi, I hope you're doing well!
Assistant: greeting

User: Can you tell me about the Aayushman Bharat scheme?
Assistant: scheme_info

User: I’ve been having chest pain and shortness of breath for two days.
Assistant: consultation

User: I want to understand my prescription.
Assistant: prescription

User: Good morning, doctor!
Assistant: greeting

User: What benefits do I get under the CGHS scheme?
Assistant: scheme_info

User: I have a sore throat and slight fever since last night. Should I be worried?
Assistant: consultation

User: I want to know about medicines from my prescription?
Assistant: prescription

User: Thanks for your help!
Assistant: greeting

User: How do I apply for the state medical reimbursement program?
Assistant: scheme_info

User: I’m feeling dizzy and lightheaded most of the time.
Assistant: consultation

User: I want to chat with my prescription.
Assistant: prescription
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
PRESCRIPTION_INTENT = 'prescription'


def get_intent(session_id, text):
    curr_state = _get_curr_state(session_id)
    if curr_state in [SCHEME_INTENT, CONSULTATION_INTENT, PRESCRIPTION_INTENT]:
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
        response = _handle_llama_31_405b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=ENGLISH)

        if 'greeting' in response:
            intent = GREETING_INTENT
        elif 'scheme_info' in response:
            intent = SCHEME_INTENT
        elif 'consultation' in response:
            intent = CONSULTATION_INTENT
        elif 'prescription' in response:
            intent = PRESCRIPTION_INTENT

        _update_curr_state(session_id=session_id, state=intent)
        return intent


def get_audio_intent(session_id, audio_path, language):

    curr_state = _get_curr_state(session_id)
    print("Current Path: ", os.getcwd())
    print("Audio Path: ", audio_path)
    if curr_state in [SCHEME_INTENT, CONSULTATION_INTENT, PRESCRIPTION_INTENT]:
        return curr_state
    else:
        text = get_text(audio_path, language=language)
        messages = [
            FactoryConfig.llm.create_message(
                role="system",
                content=IP_PROMPT,
            ),
            FactoryConfig.llm.create_message(role="user", content=text),
        ]
        breakpoints = _get_breakpoints(language=ENGLISH)
        response = _handle_llama_31_405b_call_no_streaming(messages=messages, breakpoints=breakpoints, language=ENGLISH)
        if 'greeting' in response:
            intent = GREETING_INTENT
        elif 'scheme_info' in response:
            intent = SCHEME_INTENT
        elif 'consultation' in response:
            intent = CONSULTATION_INTENT
        elif 'prescription' in response:
            intent = PRESCRIPTION_INTENT

        _update_curr_state(session_id=session_id, state=intent)
        return intent


GREETING_RESPONSES = {
    ENGLISH: "Welcome! you can consult about any illness or you can know about different government medical schemes and you can also try to understand your previous prescriptions.",
    HINDI: "स्वागत है, आप किसी भी बीमारी के बारे में सलाह ले सकते हैं, विभिन्न सरकारी चिकित्सा योजनाओं के बारे में जान सकते हैं, और अपने पिछले प्रिस्क्रिप्शन को भी समझने की कोशिश कर सकते हैं।",
    TELUGU: "స్వాగతం, మీరు ఏవైనా వ్యాధుల గురించి సలహా తీసుకోవచ్చు, వివిధ ప్రభుత్వ వైద్య పథకాల గురించి తెలుసుకోవచ్చు, మరియు మీ మునుపటి ప్రిస్క్రిప్షన్‌లను కూడా అర్థం చేసుకోవడానికి ప్రయత్నించవచ్చు.",
    MARATHI: "स्वागत आहे, तुम्ही कोणत्याही आजाराबद्दल सल्ला घेऊ शकता, विविध सरकारी वैद्यकीय योजनांविषयी जाणून घेऊ शकता, आणि तुमच्या मागील प्रिस्क्रिप्शनचा अर्थ लावण्याचा प्रयत्नही करू शकता."
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
    elif intent == PRESCRIPTION_INTENT:
        get_text_response_prescription(request=request, producer=producer)


def handle_audio(request: MLRequest, producer) -> list:
    audio_path = "/mnt/shared-dir/" + request.content
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
    elif intent == PRESCRIPTION_INTENT:
        respond_back_in_audio_streaming_prescription(request=request, producer=producer)
