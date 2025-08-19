from faster_whisper import WhisperModel
import soundfile as sf
import numpy as np
import librosa

model = WhisperModel("small")

def transcribe(audio_path):
    data, sr = sf.read(audio_path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != 16000:
        data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        sr = 16000

    segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
    text = "".join([seg.text for seg in segments]).strip()
    return text or "(no speech detected)"
