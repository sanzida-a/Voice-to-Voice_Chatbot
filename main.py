import os
import json
import difflib
import time
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from TTS.api import TTS
from serpapi import GoogleSearch
from dotenv import load_dotenv
import pygame
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure output directory exists
os.makedirs("audio", exist_ok=True)

# 1. Speech-to-Text (STT)
class STT:
    def __init__(self, model_name="small"):
        try:
            self.model = WhisperModel(model_name)
            logger.info("STT model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize STT model: {e}")
            raise

    def record_audio(self, duration=5, sample_rate=16000, filename="audio/input.wav"):
        try:
            logger.info("Recording audio... Speak now.")
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()
            sf.write(filename, audio, sample_rate)
            logger.info(f"Audio recorded and saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None

    def transcribe(self, audio_path):
        try:
            segments, _ = self.model.transcribe(audio_path, beam_size=5, vad_filter=True)
            text = "".join([seg.text for seg in segments]).strip()
            return text if text else "No speech detected"
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return "Error processing audio"

# 2. Text-to-Speech (TTS)
class TTSWrapper:
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        try:
            self.tts = TTS(model_name)
            logger.info("TTS model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS model: {e}")
            raise

    def speak(self, text, out_path=None):
        try:
            if not out_path:
                out_path = f"audio/reply_{int(time.time())}.wav"
            self.tts.tts_to_file(text=text, file_path=out_path)
            logger.info(f"TTS output saved to {out_path}")
            self.play_audio(out_path)
            return out_path
        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
            return None

    def play_audio(self, audio_path):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
            logger.info("Audio playback completed")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

# 3. Web Search Tool
class WebSearch:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            logger.warning("SERPAPI_API_KEY not found. Web search will not work.")

    def search(self, query, max_results=3):
        if not self.api_key:
            return [{"title": "Error", "snippet": "Web search unavailable due to missing API key", "link": ""}]
        try:
            search = GoogleSearch({"q": query, "api_key": self.api_key, "num": max_results})
            results = search.get_dict()
            output = []
            if "organic_results" in results:
                for r in results["organic_results"][:max_results]:
                    output.append({
                        "title": r.get("title", "No title"),
                        "snippet": r.get("snippet", "No snippet available"),
                        "link": r.get("link", "")
                    })
            return output
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return [{"title": "Error", "snippet": "Failed to fetch search results", "link": ""}]

    def summarize_results(self, results):
        """Summarize search results as readable sentences."""
        if not results or "Error" in results[0]["title"]:
            return "Sorry, I couldn't find any relevant information."

        summary_sentences = []
        for r in results:
            title = r.get("title", "No title")
            snippet = r.get("snippet", "No snippet available").strip()
            if snippet and not snippet.endswith("."):
                snippet += "."  
            summary_sentences.append(f"{title}: {snippet}")

        return " ".join(summary_sentences)

# 4. FAQ Tool
class FAQ:
    def __init__(self, path="faq.json"):
        self.faq = self.load_faq(path)

    def load_faq(self, path):
        try:
            if not os.path.exists(path):
                logger.warning(f"FAQ file {path} not found. Using empty FAQ.")
                return {}
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading FAQ: {e}. Using empty FAQ.")
            return {}

    def match_faq(self, user_text, cutoff=0.8):
        keys = list(self.faq.keys())
        best = difflib.get_close_matches(user_text, keys, n=1, cutoff=cutoff)
        if best:
            return self.faq[best[0]]
        return None

# 5. Chatbot
class Chatbot:
    def __init__(self):
        self.stt = STT()
        self.tts = TTSWrapper()
        self.web_search = WebSearch()
        self.faq = FAQ()

    def needs_search(self, user_text):
        search_keywords = ["latest", "current", "news", "recent", "update", "search", "right now"]
        return any(keyword in user_text.lower() for keyword in search_keywords) or user_text.lower().startswith("search:")

    def process_query(self, user_text):
        logger.info(f"Processing query: {user_text}")

        # First, try FAQ
        faq_answer = self.faq.match_faq(user_text)
        if faq_answer:
            logger.info("FAQ match found")
            return faq_answer

        # Then, web search if needed
        if self.needs_search(user_text):
            query = user_text.split("search:", 1)[-1].strip() if user_text.lower().startswith("search:") else user_text
            logger.info(f"Performing web search for: {query}")
            results = self.web_search.search(query)
            return self.web_search.summarize_results(results)

        # Default fallback
        logger.info("No FAQ or search match. Using default response.")
        return f"I'm not sure about '{user_text}'."

    def run(self):
        print("Chatbot started. Say 'quit' to exit. Speak after the prompt.")
        while True:
            input("Press Enter to record (5 seconds)...")
            audio_file = self.stt.record_audio()
            if not audio_file:
                print("Failed to record audio. Try again.")
                continue

            user_text = self.stt.transcribe(audio_file)
            print(f"[User said] {user_text}")
            if user_text.lower() == "quit":
                print("Exiting chatbot.")
                break
            if user_text in ["No speech detected", "Error processing audio"]:
                print("No speech detected or error occurred. Please try again.")
                continue

            response_text = self.process_query(user_text)
            print(f"[Bot reply] {response_text}")
            self.tts.speak(response_text)

# Main
if __name__ == "__main__":
    try:
        chatbot = Chatbot()
        chatbot.run()
    except KeyboardInterrupt:
        print("Chatbot stopped by user.")
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        print("An error occurred. Check logs for details.")
