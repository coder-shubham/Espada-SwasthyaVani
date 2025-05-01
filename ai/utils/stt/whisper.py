import sys

sys.path.append('.')

from factory.config import FactoryConfig
from factory.constants import ENGLISH

def speech_to_text(speech, language=ENGLISH):
    result = FactoryConfig.stt_pipe(speech, generate_kwargs={"language": FactoryConfig.whisper_lang_code[language]})
    return result.get('text')


# if __name__ == '__main__':
#     asr = ASR(device="cuda" if torch.cuda.is_available() else "cpu", language_code="en")

#     # Read the entire audio file into bytes
#     with open("testaudio.mp3", "rb") as f:
#         audio_data = f.read()

#     # Process the entire audio file
#     transcription = asr.process_whole_audio(audio_data)
#     print(transcription)

#     if transcription:
#         print(f"Transcription: {transcription}")
#     else:
#         print("Transcription failed.")
