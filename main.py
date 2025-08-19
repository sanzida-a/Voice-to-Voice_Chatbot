from stt import transcribe
from tts import speak
from web_search import serpapi_search, summarize_results
import json, difflib

def load_faq(path="faq.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def match_faq(user_text, faq, cutoff=0.9):
    keys = list(faq.keys())
    best = difflib.get_close_matches(user_text, keys, n=1, cutoff=cutoff)
    if best:
        return faq[best[0]]
    return None

def chatbot_response(user_text):
    faq_data = load_faq()

    # 1. FAQ
    faq_answer = match_faq(user_text, faq_data)
    if faq_answer:
        return faq_answer

    # 2. Web search
    if user_text.lower().startswith("search:"):
        query = user_text.split("search:", 1)[-1].strip()
        return summarize_results(serpapi_search(query))

    # 3. Default
    return f"Input was: \"{user_text}\". Complete'."

if __name__ == "__main__":
    # 🔹 Hardcode your audio input and output paths here
    audio_input = "audio/input.wav"   # put your file in audio/ folder
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
