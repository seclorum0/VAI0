# VAI0 — Real-time Modular Speech-to-Speech AI (CPU-only)

VAI0 is an open-source, CPU-friendly, real-time speech-to-speech AI system.  
It listens to your voice, processes it using a local LLM (via Ollama), and responds with natural-sounding speech through ElevenLabs TTS.

> Designed for real-time, modular, and local-first applications — no GPU required.

---

## ✨ Features

- 🎙️ Voice input via Google Speech Recognition (Indonesian & English)
- 🧠 Local LLM inference using [Ollama](https://ollama.com/)
- 🗣️ Text-to-Speech via [ElevenLabs API](https://www.elevenlabs.io/)
- 🔊 Real-time audio playback with `pygame.mixer`
- 🌐 Modular code structure (Speech → LLM → TTS)
- 🧩 PyQt5-based minimalist GUI with dynamic voice visualizer
- ✅ CPU-Only: No GPU or heavy compute requirements

---

## 🧠 How It Works

1. 🎤 Record voice from microphone  
2. 🧠 Transcribe with Google Speech Recognition  
3. 💬 Send prompt to local LLM (e.g., `llama2` via Ollama)  
4. 🔁 Convert LLM response to voice via ElevenLabs  
5. 🔊 Play the result instantly

---

## 🚀 Getting Started

Follow these steps to spin-up **VAI0** on your local machine (CPU-only):

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/VAI0.git
   cd VAI0
   
2. **Install Python dependencies**
    ```bash
    pip install -r requirements.txt

3. **Install & run Ollama(for local LLM)**
    ```bash
    ollama run llama2   # or any model you like

4. **Setup your Elevenlabs API key**
    Open config.py and replace the placeholder:
    ```python
    ELEVENLABS_API_KEY = "your-api-key-here"

5. **Launch VAI0**
    ```bash
    python vai0.py

6. **(Optional) test individual modules**
    ```bash
    python speech_to_text.py     # microphone → text
    python test_ollama.py        # quick LLM chat
    python test_elevenlabs.py    # generate & play TTS audio


## 📦 Requirements

See [`requirements.txt`](./requirements.txt) for full list.

Install with:

```bash
pip install -r requirements.txt
