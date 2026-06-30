"""
sarvam_voice.py — STT (saaras:v3) + TTS (bulbul:v3) via Sarvam API
"""

import os
import base64
import requests
from dotenv import load_dotenv
from config import (
    SARVAM_API_BASE,
    STT_MODEL,
    STT_WITH_DISFLUENCIES,
    TTS_MODEL,
    TTS_SPEAKER,
    TTS_LANGUAGE,
    TTS_PITCH,
    TTS_PACE,
    TTS_LOUDNESS,
)

load_dotenv()

STT_URL = f"{SARVAM_API_BASE}/speech-to-text"
TTS_URL = f"{SARVAM_API_BASE}/text-to-speech"


def _api_key() -> str:
    key = os.environ.get("SARVAM_API_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "SARVAM_API_KEY not set. Add it to .env — free key at https://dashboard.sarvam.ai"
        )
    return key


# ── SPEECH TO TEXT ────────────────────────────────────────────
def speech_to_text(
    audio_bytes: bytes,
    filename: str = "audio.wav",
    language_code: str = "unknown",   # FIX: now accepts language param
) -> str:
    """
    Transcribe audio to text using Sarvam Saaras v3.
    language_code: "unknown" = auto-detect, or e.g. "hi-IN", "ta-IN"
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "wav"
    mime_map = {
        "wav":  "audio/wav",
        "mp3":  "audio/mpeg",
        "ogg":  "audio/ogg",
        "flac": "audio/flac",
        "m4a":  "audio/mp4",
        "webm": "audio/webm",
    }
    mime = mime_map.get(ext, "audio/wav")

    files   = {"file": (filename, audio_bytes, mime)}
    data    = {
        "model":             STT_MODEL,
        "language_code":     language_code,
        "with_disfluencies": str(STT_WITH_DISFLUENCIES).lower(),
    }
    headers = {"api-subscription-key": _api_key()}

    try:
        resp = requests.post(STT_URL, headers=headers, files=files, data=data, timeout=60)
        resp.raise_for_status()
        print("STT raw response:", resp.json())  
        transcript = resp.json().get("transcript", "").strip()
        return transcript if transcript else "⚠️ No speech detected in audio."
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        if status == 401:
            return "❌ Invalid API key. Check SARVAM_API_KEY in .env"
        if status == 413:
            return "❌ Audio too large (max 25 MB)."
        return f"❌ STT error {status}: {e}"
    except Exception as e:
        return f"❌ STT error: {e}"


# ── TEXT TO SPEECH ────────────────────────────────────────────
def text_to_speech(
    text:          str,
    speaker:       str   = TTS_SPEAKER,
    language_code: str   = TTS_LANGUAGE,
    pitch:         int   = TTS_PITCH,
    pace:          float = TTS_PACE,
    loudness:      float = TTS_LOUDNESS,
) -> bytes | None:
    """Convert text to speech using Sarvam Bulbul v3."""
    if not text or not text.strip():
        return None

    # Map language to correct official Sarvam speaker
    speaker_map = {
        "hi-IN": "shubh",
        "en-IN": "ritu",
        "en-IN": "priya",
        "ta-IN": "kavya",
        "ml-IN": "suhani",
        "te-IN": "vijay",
    }
    safe_speaker = speaker_map.get(language_code, "shubh")

    chunks = _chunk_tts_text(text, max_len=500)
    headers = {
        "api-subscription-key": _api_key(),
        "Content-Type": "application/json",
    }
    all_audio = b""

    for chunk in chunks:
        payload = {
            "text":                 chunk,
            "target_language_code": language_code,
            "speaker":              safe_speaker,
            "model":                TTS_MODEL,
            "pace":                 pace,
            "speech_sample_rate":   22050,
        }
        try:
            resp = requests.post(TTS_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            audios = resp.json().get("audios", [])
            if audios:
                wav = base64.b64decode(audios[0])
                all_audio = wav if not all_audio else all_audio + wav[44:]
        except Exception as e:
            print(f"TTS chunk error: {e}")
            return None

    return all_audio if all_audio else None


def _chunk_tts_text(text: str, max_len: int = 500) -> list:
    """Split text into sentence-aware chunks of <= max_len chars."""
    if len(text) <= max_len:
        return [text]
    chunks, current = [], ""
    for sentence in text.replace("\n", " ").split(". "):
        sentence = sentence.strip()
        if not sentence:
            continue
        if not sentence.endswith("."):
            sentence += "."
        if len(current) + len(sentence) + 1 <= max_len:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks if chunks else [text[:max_len]]
