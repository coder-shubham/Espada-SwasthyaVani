import io
import json
import requests
import soundfile as sf
from playsound3 import playsound
import base64
import os

import numpy as np
import uuid

import sys
sys.path.append('.')

from factory.config import FactoryConfig
from factory.config import HINDI, ENGLISH, TELUGU, MARATHI


def _prepare_payload(text, language):

    codes = dict()
    codes = {
        HINDI: 'hi',
        ENGLISH: 'en',
        TELUGU: 'te',
        MARATHI: 'mr'
    }

    payload = json.dumps({
    "inputs": [
    {
    "name": "INPUT_TEXT",
    "shape": [
        1
    ],
    "datatype": "BYTES",
    "data": [
        text
    ]
    },
    {
    "name": "INPUT_SPEAKER_ID",
    "shape": [
        1
    ],
    "datatype": "BYTES",
    "data": [
        "female"
    ]
    },
    {
    "name": "INPUT_LANGUAGE_ID",
    "shape": [
        1
    ],
    "datatype": "BYTES",
    "data": [
        codes[language]
    ]
    }
    ]
    })
    return payload

def get_audio_using_tts(text, language):
    payload = _prepare_payload(text, language=language)
    headers = {
        'authorization': f'Bearer {FactoryConfig.indic_tts_token}', # replace with your API token
        'content-type': 'application/json'
    }
    response = requests.request("POST", url=FactoryConfig.indic_tts_url, headers=headers, data=payload)

    if response.status_code == 200:
        DEFAULT_SAMPLING_RATE = 24000
        audio_arr = json.loads(response.text)["outputs"][0]["data"]
        # _id = str(uuid.uuid4())
        # sf.write(f'temp_audio_{_id}.wav', audio_arr, DEFAULT_SAMPLING_RATE)
        # playsound(f'temp_audio_{_id}.wav')
        # os.remove(f'temp_audio_{_id}.wav')
        
        buffer = io.BytesIO()
        sf.write(buffer, audio_arr, DEFAULT_SAMPLING_RATE, format='WAV')
        buffer.seek(0)
        audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return audio_base64