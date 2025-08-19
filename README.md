# Voice-to-Voice Chatbot with Web Search and FAQ Tools

This project implements a **voice-to-voice chatbot** that processes voice input, responds using text-to-speech (TTS), and answers queries using a local FAQ tool or a web search tool. It uses open-source models for speech-to-text (STT) and TTS, and integrates with SerpAPI for web searches. The chatbot handles FAQ lookups, web searches for recent information, and default conversational responses.

---

## Features

- **Speech-to-Text (STT):** Converts voice input to text using the `faster-whisper` model.
- **Text-to-Speech (TTS):** Generates voice output using the Coqui TTS model (`tts_models/en/ljspeech/tacotron2-DDC`).
- **FAQ Tool:** Answers predefined questions stored in `faq.json`, with fuzzy matching.
- **Web Search Tool:** Fetches recent information via SerpAPI, with summarized results for concise TTS output.
- **Live Audio Recording:** Records voice input from the microphone using `sounddevice`.
- **Audio Playback:** Plays responses using `pygame` for a complete voice-to-voice experience.
- **Continuous Interaction:** Runs in a loop, allowing multiple queries until the user says `"quit"`.


---

## Installation

### Clone the Repository
```bash
git clone https://github.com/sanzida-a/Voice-to-Voice_Chatbot.git
cd Voice-to-Voice_Chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

```

---

Interact with the Chatbot

1. Press Enter to start recording a 5-second audio clip via your microphone.

2. Speak your query, e.g., "What is AI?", "Latest tech news", or "Hello".

4. The chatbot processes the input:

    Checks faq.json for a matching answer.

    Performs a web search for queries with keywords like "latest", "news", or "search:".

    Returns a default response for unmatched queries.

    The response is converted to speech and played back.

5. Say "quit" to exit the chatbot.

---

## Notes

Character Limit: Web search results are capped at 250 characters for concise TTS output. Adjust in WebSearch.summarize_results if needed.

Error Handling: Handles missing files, invalid API keys, and audio processing errors gracefully.

Logging: Debug information is logged to the console (model initialization, errors).

### Customization:

Modify faq.json to add or update FAQ entries.

Adjust recording duration in STT.record_audio.

Change the TTS model in TTSWrapper.__init__ if desired.