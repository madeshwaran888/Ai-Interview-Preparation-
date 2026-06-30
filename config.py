"""
config.py — All tuneable knobs in one place
"""

# ── Sarvam API ─────────────────────────────────────────────────
SARVAM_API_BASE   = "https://api.sarvam.ai"

# Chat LLM
SARVAM_CHAT_MODEL = "sarvam-30b"
# SARVAM_CHAT_MODEL = "sarvam-105b"  # Uncomment for max accuracy

# Speech-to-Text
STT_MODEL             = "saaras:v3"
STT_LANGUAGE          = "unknown"       # auto-detect
STT_WITH_DISFLUENCIES = False

# Text-to-Speech
TTS_MODEL    = "bulbul:v3"
TTS_SPEAKER  = "anushka"
TTS_LANGUAGE = "en-IN"
TTS_PITCH    = 0
TTS_PACE     = 1.0
TTS_LOUDNESS = 1.5

# ── RAG / Embedding ───────────────────────────────────────────
EMBED_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CHROMA_PATH  = "./chroma_db"
COLLECTION   = "interview_prep"
CHUNK_SIZE    = 400
CHUNK_OVERLAP = 80
TOP_K         = 6
RERANK_TOP_N  = 3

# ── Generation params ─────────────────────────────────────────
MAX_TOKENS_ANSWER   = 2048
MAX_TOKENS_QUESTION = 512
MAX_TOKENS_EVAL     = 1024
TEMPERATURE_ANSWER  = 0.3
TEMPERATURE_MOCK    = 0.7
TEMPERATURE_EVAL    = 0.2

# ── TTS Speakers  (label → (speaker_id, language_code)) ───────
# FIX: Added 7 languages as requested
TTS_SPEAKERS = {
    "Shubh   — Hindi (hi-IN)":            ("shubh",    "hi-IN"),
    "Ritu    — English (en-IN)":          ("ritu",     "en-IN"),
    "Priya   — English (en-IN)":          ("priya",    "en-IN"),
    "Kavya   — Tamil (ta-IN)":            ("kavya",    "ta-IN"),
    "Vijay   — Telugu (te-IN)":           ("vijay",    "te-IN"),
    "Suhani  — Malayalam (ml-IN)":        ("suhani",   "ml-IN"),
}

# ── STT Language selector (for voice chat tab) ─────────────────
# FIX: 7 languages added as requested
STT_LANGUAGES = {
    "Auto Detect":          "unknown",
    "English (en-IN)":      "en-IN",
    "Hindi (hi-IN)":        "hi-IN",
    "Tamil (ta-IN)":        "ta-IN",
    "Telugu (te-IN)":       "te-IN",
    "Kannada (kn-IN)":      "kn-IN",
    "Bengali (bn-IN)":      "bn-IN",
    "Gujarati (gu-IN)":     "gu-IN",
    "Marathi (mr-IN)":      "mr-IN",
    "Malayalam (ml-IN)":    "ml-IN",
}
