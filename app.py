"""
JARVIS v2 — AI Interview Prep
app.py — Streamlit UI

Run:  streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv
import os

from pipeline import (
    index_document,
    ask,
    mock_question,
    evaluate,
    get_collection_count,
    clear_knowledge_base,
)
from sarvam_voice import speech_to_text, text_to_speech
from config import SARVAM_CHAT_MODEL, TTS_SPEAKERS, STT_LANGUAGES

load_dotenv()

# ── Page config — MUST be first Streamlit call ────────────────
st.set_page_config(
    page_title="JARVIS v2 – Interview Prep",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────
DEFAULTS = {
    "rag_query":        "",
    "mock_question":    None,
    "mock_feedback":    None,
    "tts_speaker":      "Arjun",
    "tts_language":     "en-ta",
    "tts_pace":         1.0,
    "voice_transcript": "",
    "voice_answer":     "",
    "stt_language":     "unknown",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🎯 JARVIS v2")
    st.caption(f"Chat: `{SARVAM_CHAT_MODEL}` · STT: `saaras:v3` · TTS: `bulbul:v3`")

    # ── API Key ───────────────────────────────────────────────
    st.divider()
    st.subheader("🔑 Sarvam API Key")
    api_key_val = os.environ.get("SARVAM_API_KEY", "")
    api_input = st.text_input(
        "Sarvam API Key",
        value=api_key_val,
        type="password",
        placeholder="Paste key from.sarvam.ai",
        help="Free key at https://sarvam.ai",
    )
    if api_input.strip():
        os.environ["SARVAM_API_KEY"] = api_input.strip()
        st.success("✅ API key set")
    else:
        st.warning("⚠️ No API key — all features disabled")

    # ── Knowledge Base ────────────────────────────────────────
    st.divider()
    st.header("📁 Knowledge Base")
    chunk_count = get_collection_count()
    if chunk_count > 0:
        st.success(f"✅ {chunk_count} chunks indexed")
    else:
        st.warning("No documents indexed yet.")

    st.subheader("Upload Resume")
    resume_file = st.file_uploader("Resume (PDF)", type=["pdf"], key="resume_upload")
    if resume_file and st.button("Index Resume", use_container_width=True):
        with st.spinner("Reading, chunking & embedding…"):
            n = index_document(resume_file.read(), "pdf", "resume")
        st.success(f"Indexed {n} chunks from resume!")
        st.rerun()

    st.subheader("Upload Interview Q&A")
    qa_file = st.file_uploader("Question bank (.txt)", type=["txt"], key="qa_upload")
    if qa_file and st.button("Index Q&A File", use_container_width=True):
        with st.spinner("Embedding…"):
            n = index_document(qa_file.read(), "txt", "qa_dataset")
        st.success(f"Indexed {n} chunks!")
        st.rerun()

    if st.button("🗑️ Reset Knowledge Base", type="secondary", use_container_width=True):
        clear_knowledge_base()
        st.success("Knowledge base cleared.")
        st.rerun()

    # ── Voice Settings ────────────────────────────────────────
    st.divider()
    st.header("🔊 Voice Settings")
    st.caption("Controls Read Aloud and Voice Chat tab")

    # TTS Speaker + language (7 languages)
    speaker_label = st.selectbox(
        "🗣️ Speaker / Language",
        options=list(TTS_SPEAKERS.keys()),
        index=0,
        help="Choose voice and language for Text-to-Speech",
    )
    st.session_state.tts_speaker, st.session_state.tts_language = TTS_SPEAKERS[speaker_label]

    # STT Language (for voice recording)
    stt_label = st.selectbox(
        "🎙️ Recording Language",
        options=list(STT_LANGUAGES.keys()),
        index=0,
        help="Select the language you will speak in. Auto Detect works for most cases.",
    )
    st.session_state.stt_language = STT_LANGUAGES[stt_label]

    st.session_state.tts_pace = st.slider(
        "Speaking pace",
        min_value=0.5, max_value=2.0,
        value=float(st.session_state.tts_pace),
        step=0.1,
        help="1.0 = natural speed",
    )

    st.caption(
        "📚 [Sarvam Docs](https://docs.sarvam.ai) · "
        "[Dashboard](https://sarvam.ai)"
    )


# ════════════════════════════════════════════════════════════════
# HELPER: TTS "Read Aloud" button
# ════════════════════════════════════════════════════════════════
def tts_button(text: str, key: str) -> None:
    """Render a 🔊 Read Aloud button."""
    if st.button("🔊 Read Aloud", key=key):
        with st.spinner("Generating audio…"):
            audio = text_to_speech(
                text,
                speaker=st.session_state.tts_speaker,
                language_code=st.session_state.tts_language,
                pace=st.session_state.tts_pace,
            )
        if audio:
            st.audio(audio, format="audio/wav")
        else:
            st.error("TTS failed — check your API key.")


# ════════════════════════════════════════════════════════════════
# MAIN HEADER
# ════════════════════════════════════════════════════════════════
st.title("🎯 JARVIS v2 — AI Interview Prep")
st.caption(
    "RAG · Sarvam-30B · ChromaDB · Saaras v3 STT · Bulbul v3 TTS · sentence-transformers"
)
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Ask Questions",
    "🎤 Mock Interview",
    "📝 Evaluate Answer",
    "🗣️ Voice Chat",
])


# ════════════════════════════════════════════════════════════════
# TAB 1 — ASK QUESTIONS
# ════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Ask anything about interviews")
    quick_prompts = [
        "Generate 5 ML interview questions",
        "What are common Python interview questions?",
        "Explain Big-O notation with examples",
        "What system design questions are asked at FAANG?",
        "What should I say about strengths and weaknesses?",
        "Generate questions tailored to my resume",
    ]
    st.write("**Quick-start prompts:**")
    btn_cols = st.columns(3)
    for i, prompt in enumerate(quick_prompts):
        if btn_cols[i % 3].button(prompt, key=f"qp_{i}", use_container_width=True):
            st.session_state["rag_query"] = prompt

    query = st.text_input(
        "Your question:",
        value=st.session_state.get("rag_query", ""),
        placeholder="e.g. What is the difference between a list and a tuple?",
        key="rag_query_input",
    )
    show_chunks = st.checkbox("Show retrieved context chunks", value=False)

    if st.button("Ask →", type="primary", key="ask_btn") and query.strip():
        with st.spinner("Searching knowledge base & generating answer…"):
            answer, chunks = ask(query)
        st.markdown("### Answer")
        st.markdown(answer)
        tts_button(answer, key="tts_tab1")

        if show_chunks and chunks:
            with st.expander(f"📄 Retrieved context ({len(chunks)} chunks)"):
                for i, c in enumerate(chunks, 1):
                    st.text_area(f"Chunk {i}", c, height=120, key=f"ctx_chunk_{i}")


# ════════════════════════════════════════════════════════════════
# TAB 2 — MOCK INTERVIEW
# ════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Mock Interview Session")
    left, right = st.columns([1, 2])

    with left:
        topic = st.selectbox(
            "Topic",
            ["Python", "Machine Learning", "Deep Learning", "System Design",
             "SQL & Databases", "Algorithms & Data Structures",
             "Behavioural (STAR method)", "From my resume"],
        )
        difficulty = st.select_slider(
            "Difficulty",
            options=["Junior", "Mid-level", "Senior", "Staff / Principal"],
            value="Mid-level",
        )
        if st.button("Generate Question 🎲", type="primary", use_container_width=True):
            full_topic = f"{difficulty} {topic}"
            with st.spinner(f"Generating {full_topic} question…"):
                q = mock_question(full_topic)
            st.session_state["mock_question"] = q
            st.session_state.pop("mock_feedback", None)

    with right:
        if st.session_state.get("mock_question"):
            q_text = st.session_state["mock_question"]
            st.info(f"**Question:** {q_text}")
            tts_button(q_text, key="tts_mock_q")

            user_ans = st.text_area(
                "Your answer:",
                height=180,
                placeholder="Treat this as a real interview — take a moment to think.",
                key="mock_answer_input",
            )
            if st.button("Submit & Get Feedback →", type="primary"):
                if not user_ans.strip():
                    st.warning("Please write an answer before submitting.")
                else:
                    with st.spinner("Evaluating your answer…"):
                        feedback = evaluate(q_text, user_ans)
                    st.session_state["mock_feedback"] = feedback

        if st.session_state.get("mock_feedback"):
            st.markdown("### Feedback")
            fb = st.session_state["mock_feedback"]
            st.markdown(fb)
            tts_button(fb, key="tts_mock_fb")

        elif not st.session_state.get("mock_question"):
            st.info("← Generate a question to begin your mock interview.")


# ════════════════════════════════════════════════════════════════
# TAB 3 — EVALUATE ANSWER
# ════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Evaluate Your Answer")
    st.caption("Paste any interview question and your answer to get structured feedback.")

    question_input = st.text_input(
        "Interview question:",
        placeholder="e.g. Explain the difference between bagging and boosting.",
        key="eval_question",
    )
    answer_input = st.text_area(
        "Your answer:",
        height=200,
        placeholder="Write your answer here…",
        key="eval_answer_input",
    )

    if st.button("Evaluate →", type="primary", key="eval_btn"):
        if not question_input.strip() or not answer_input.strip():
            st.warning("Please fill in both the question and your answer.")
        else:
            with st.spinner("Evaluating…"):
                result = evaluate(question_input, answer_input)
            st.markdown("### Evaluation")
            st.markdown(result)
            tts_button(result, key="tts_eval")


# ════════════════════════════════════════════════════════════════
# TAB 4 — VOICE CHAT
# FIX: last block was outside 'with tab4' — moved inside
# FIX: indentation of entire block corrected
# ════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🗣️ Voice Chat")
    st.caption(
        "Speak your question → Saaras v3 transcribes → "
        "Sarvam-30B answers → Bulbul v3 reads it back."
    )
    st.info(
        "**How to use:**\n"
        "1. Select your speaking language in the sidebar (Recording Language)\n"
        "2. Click the mic button, speak your question, click stop\n"
        "3. JARVIS auto-transcribes, answers, and reads aloud"
    )

    # Language hint
    stt_lang_display = st.session_state.get("stt_language", "unknown")
    st.caption(f"🎙️ Recording language set to: `{stt_lang_display}`")

    # ── Record voice ─────────────────────────────────────────
    st.markdown("#### 🎤 Record Your Question")
    recorded = st.audio_input("Click the mic, speak, then click stop")

    if recorded:
        st.audio(recorded)
        with st.spinner("Transcribing your voice…"):
            transcript = speech_to_text(
                recorded.getvalue(),
                "recording.wav",
                language_code=st.session_state.stt_language,   # FIX: pass selected language
            )
        st.session_state.voice_transcript = transcript

        if transcript and not transcript.startswith("❌") and not transcript.startswith("⚠️"):
            st.success(f"📝 You said: **{transcript}**")

            with st.spinner("JARVIS is thinking…"):
                answer_text, chunks = ask(transcript)
            st.session_state.voice_answer = answer_text

            st.markdown("### 💬 Answer")
            st.markdown(answer_text)

            with st.spinner("Converting answer to speech…"):
                audio_bytes = text_to_speech(
                    answer_text,
                    speaker=st.session_state.tts_speaker,
                    language_code=st.session_state.tts_language,
                    pace=st.session_state.tts_pace,
                )
            if audio_bytes:
                st.markdown("#### 🔊 JARVIS Speaking")
                st.audio(audio_bytes, format="audio/wav", autoplay=True)
            else:
                st.warning("⚠️ TTS failed. Read the text answer above.")

            if chunks:
                with st.expander(f"📄 Context used ({len(chunks)} chunks)"):
                    for i, c in enumerate(chunks, 1):
                        st.text_area(f"Chunk {i}", c, height=100, key=f"vc_chunk_{i}")
        else:
            st.error(transcript)

    # ── Show previous answer ──────────────────────────────────
    # FIX: this block was outside 'with tab4' — now correctly indented inside
    elif st.session_state.voice_answer:
        st.markdown("### 💬 Previous Answer")
        st.markdown(st.session_state.voice_answer)
        tts_button(st.session_state.voice_answer, key="tts_voice_prev")
