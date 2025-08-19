# main.py

from faster_whisper import WhisperModel
import soundfile as sf
import numpy as np
import librosa
from TTS.api import TTS
import os, json, difflib
from serpapi import GoogleSearch
from dotenv import load_dotenv


# -----------------------------
# 1. Speech-to-Text (STT)
# -----------------------------
model = WhisperModel("small")

def transcribe(audio_path):
    data, sr = sf.read(audio_path)
    if data.ndim > 1:
        data = data.mean(axis=1)  # convert stereo -> mono
    if sr != 16000:
        data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        sr = 16000

    segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
    text = "".join([seg.text for seg in segments]).strip()
    return text or "(no speech detected)"


# -----------------------------
# 2. Text-to-Speech (TTS)
# -----------------------------
EN_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"
_tts = TTS(EN_MODEL)

def speak(text, out_path="bot_reply.wav"):
    _tts.tts_to_file(text=text, file_path=out_path)
    return out_path


# -----------------------------
# 3. Web Search Tool
# -----------------------------
load_dotenv()  # load SERPAPI_API_KEY from .env

def serpapi_search(query, max_results=5):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("❌ SERPAPI_API_KEY not found in .env")

    search = GoogleSearch({
        "q": query,
        "api_key": api_key,
        "num": max_results
    })
    results = search.get_dict()

    output = []
    if "organic_results" in results:
        for r in results["organic_results"][:max_results]:
            output.append({
                "title": r.get("title", "No title"),
                "link": r.get("link", ""),
                "snippet": r.get("snippet", "No snippet available")
            })
    return output

def summarize_results(results):
    if not results:
        return "No results found."
    return "\n".join([
        f"{i+1}. {r['title']} - {r['snippet']} (Source: {r['link']})"
        for i, r in enumerate(results)
    ])


# -----------------------------
# 4. FAQ Tool
# -----------------------------
def load_faq(path="faq.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def match_faq(user_text, faq, cutoff=0.9):
    keys = list(faq.keys())
    best = difflib.get_close_matches(user_text, keys, n=1, cutoff=cutoff)
    if best:
        return faq[best[0]]
    return None


# -----------------------------
# 5. Chatbot Logic (assignment order)
# -----------------------------
def chatbot_response(user_text):
    faq_data = load_faq()

    # Step 1: FAQ
    faq_answer = match_faq(user_text, faq_data)
    if faq_answer:
        return faq_answer

    # Step 2: Web search (only if no FAQ)
    if user_text.lower().startswith("search:"):
        query = user_text.split("search:", 1)[-1].strip()
        return summarize_results(serpapi_search(query))

    # Step 3: Default reply
    return f"You said: \"{user_text}\". I don't have an answer for that yet."


# -----------------------------
# 6. Main Program
# -----------------------------
if __name__ == "__main__":
    audio_input = "audio/input.wav"   # Put your voice file here
    audio_output = "audio/reply.wav"

    # Step 1: STT
    user_text = transcribe(audio_input)
    print("[User said]", user_text)

    # Step 2: Chatbot logic
    response_text = chatbot_response(user_text)
    print("[Bot reply]", response_text)

    # Step 3: TTS
    speak(response_text, audio_output)
    print(f"[Reply saved at] {audio_output}")
