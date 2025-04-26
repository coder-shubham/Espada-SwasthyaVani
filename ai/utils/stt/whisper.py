import sys

sys.path.append('.')
from factory.config import FactoryConfig

def speech_to_text(speech, language='hindi'):
    result = FactoryConfig.stt_pipe(speech, generate_kwargs={"language": language})
    return result.get('text')

speech_to_text('testaudio.mp3')





# The code snippet enclosed in `if __name__ == '__main__':` is a common Python idiom used to ensure
# that the code block within it only runs if the script is executed directly, and not when it is
# imported as a module in another script.
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
