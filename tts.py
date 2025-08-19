from TTS.api import TTS

EN_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"

_tts = TTS(EN_MODEL)

def speak(text, out_path="bot_reply.wav"):
    _tts.tts_to_file(text=text, file_path=out_path)
    return out_path
