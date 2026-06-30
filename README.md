# 🎯 JARVIS v2 — AI Interview Prep with Voice

RAG-powered interview preparation chatbot built on **Sarvam AI** — India's sovereign AI platform.  
Runs locally with **Streamlit** in VS Code.

---

## 🆕 What's New in v2 vs v1

| Feature | v1 | v2 |
|---|---|---|
| Chat LLM | HuggingFace Llama-3-8B | ✅ **Sarvam-30B** (Indian AI, faster, free) |
| Speech-to-Text | ❌ Not available | ✅ **Saaras v3** (23 languages, auto-detect) |
| Text-to-Speech | ❌ Not available | ✅ **Bulbul v3** (10 Indian langs + English) |
| API Keys needed | `HF_TOKEN` | ✅ ONE key: `SARVAM_API_KEY` |
| Voice Chat tab | ❌ | ✅ **Record → Transcribe → Answer → Read aloud** |
| Read Aloud buttons | ❌ | ✅ On every LLM answer (tabs 1, 2, 3) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    app.py  (Streamlit UI)                    │
│  Tab 1: Ask Questions  Tab 2: Mock Interview                 │
│  Tab 3: Evaluate       Tab 4: Voice Chat  ← NEW             │
└──────┬────────────────────────────┬──────────────────────────┘
       │                            │
       ▼                            ▼
┌──────────────────┐     ┌──────────────────────────────────┐
│  pipeline.py     │     │  sarvam_voice.py  (NEW)          │
│  index_document  │     │                                  │
│  ask()           │     │  speech_to_text()                │
│  mock_question() │     │    POST /speech-to-text          │
│  evaluate()      │     │    Model: saaras:v3              │
└──────┬───────────┘     │    Returns: transcript str       │
       │                 │                                  │
       ▼                 │  text_to_speech()                │
┌──────────────────┐     │    POST /text-to-speech          │
│  generator.py    │     │    Model: bulbul:v3              │
│  Sarvam-30B LLM  │     │    Returns: WAV bytes            │
│  /chat/completions│    └──────────────────────────────────┘
└──────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  retriever.py               │
│  embed query → ChromaDB     │
│  re-rank with CrossEncoder  │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  ChromaDB vector store      │
│  (./chroma_db)              │
└─────────────────────────────┘
```

---

## 🚀 Quick Start (5 minutes)

### Step 1 — Get your free Sarvam API key
1. Go to **[dashboard.sarvam.ai](https://dashboard.sarvam.ai)**
2. Sign up (free, no credit card)
3. Copy your **API Subscription Key**

> **One key** unlocks Chat + STT + TTS — all free tier!

### Step 2 — Set up in VS Code
```bash
# Open folder in VS Code
code .

# Create and activate virtualenv
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Add your key
```bash
cp .env.example .env
# Open .env and replace: your_sarvam_api_key_here → your real key
```

### Step 4 — Run it!
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
jarvis_v2/
│
├── app.py               ← Streamlit UI (4 tabs, sidebar, voice)
├── generator.py         ← Sarvam-30B LLM calls via REST
├── sarvam_voice.py      ← NEW: STT (saaras:v3) + TTS (bulbul:v3)
├── pipeline.py          ← Orchestrates RAG: index/ask/mock/evaluate
├── retriever.py         ← Vector search + CrossEncoder re-rank
├── embedder.py          ← Sentence-transformers + ChromaDB storage
├── chunker.py           ← RecursiveCharacterTextSplitter
├── loader.py            ← PDF (PyMuPDF) + TXT file reader
├── config.py            ← All tunable constants in one place
│
├── chroma_db/           ← Local vector DB (auto-created)
├── data/                ← Sample interview Q&A dataset
│
├── .env.example         ← Copy to .env and add your key
├── requirements.txt
└── README.md
```

---

## 🤖 Sarvam Models Used

| Feature | Model | Why |
|---|---|---|
| **Chat / RAG** | `sarvam-30b` | Fast, free-tier friendly, 30B MoE (2.4B active), best Indic language LLM |
| **Speech-to-Text** | `saaras:v3` | 23 languages, auto language detect, handles Indian accents |
| **Text-to-Speech** | `bulbul:v3` | Natural Indian voices, 10 languages, multiple speakers |

### Upgrade to highest accuracy
In `config.py`:
```python
SARVAM_CHAT_MODEL = "sarvam-105b"   # 105B flagship model
```

---

## 🗣️ Voice Chat — How It Works

```
User speaks / uploads audio
       ↓
POST /speech-to-text  (saaras:v3)
       ↓ transcript text
Edit if needed in the text box
       ↓
RAG pipeline: retrieve chunks → sarvam-30b generates answer
       ↓ answer text
POST /text-to-speech  (bulbul:v3)
       ↓ WAV bytes
st.audio(autoplay=True)  — plays in browser
```

### Supported Audio Formats (STT)
WAV · MP3 · OGG · FLAC · M4A · WEBM (max 25 MB)

### Available TTS Voices
| Speaker | Language | Gender |
|---|---|---|
| anushka | en-IN | Female |
| meera | hi-IN | Female |
| arvind | en-IN | Male |
| amol | hi-IN | Male |
| arjun | en-IN | Male |

---

## 🔧 Customisation

**Change TTS language** — edit `config.py`:
```python
TTS_LANGUAGE = "ta-IN"   # Tamil
TTS_LANGUAGE = "te-IN"   # Telugu
TTS_LANGUAGE = "kn-IN"   # Kannada
```

**Auto-load the Q&A dataset on startup** — upload `data/interview_questions.txt` via sidebar.

**Deploy to Streamlit Cloud** — push to GitHub, connect at share.streamlit.io, add `SARVAM_API_KEY` in Secrets.

---

## 📚 Resources
- [Sarvam API Docs](https://docs.sarvam.ai)
- [Free API Dashboard](https://dashboard.sarvam.ai)
- [Saaras STT Docs](https://docs.sarvam.ai/api-reference-docs/getting-started/models/saaras)
- [Bulbul TTS Docs](https://docs.sarvam.ai/api-reference-docs/getting-started/models/bulbul)
- [Sarvam-30B Model](https://docs.sarvam.ai/api-reference-docs/getting-started/models/sarvam-30b)
