
import sys
sys.path.append('.')
from factory.config import HINDI, ENGLISH, MARATHI, TELUGU, FactoryConfig


def get_text(file_path, language):
    codes = {
        HINDI: 'Hindi',
        ENGLISH: 'English',
        MARATHI: 'Marathi',
        TELUGU: 'Telugu'
    }
    data = {"input": file_path,
            "language": codes.get(language),
            "task": "transcribe",
            "max_new_tokens": 420,
            "return_timestamps": "none"
    }

    response = FactoryConfig.tir_client.infer(model_name="whisper-large-v3", data=data)
    print(response)
    if response and len(response) >=2 and response[0] == True:
        try:
            return response[1].outputs[0].data[0].strip()
        except:
            return ''