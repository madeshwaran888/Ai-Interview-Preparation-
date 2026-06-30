"""
╔══════════════════════════════════════════════════════════════╗
║   JARVIS v2 — GENERATOR                                     ║
║   generator.py  ·  Stage: LLM calls via Sarvam Chat API    ║
╚══════════════════════════════════════════════════════════════╝

WHAT CHANGED FROM v1:
  • Replaced HuggingFace InferenceClient with direct Sarvam REST calls
  • Auth header: "api-subscription-key" (not "Authorization: Bearer")
  • Endpoint: POST https://api.sarvam.ai/chat/completions
  • Same 3 functions: generate_rag_answer, generate_mock_question, evaluate_answer

API FORMAT (OpenAI-compatible):
  POST /chat/completions
  Body: { model, messages: [{role, content}], temperature, max_tokens }
  Response: { choices: [{ message: { content: "..." } }] }
"""
import os
import requests
from dotenv import load_dotenv
from config import (
    SARVAM_API_BASE,
    SARVAM_CHAT_MODEL,
    MAX_TOKENS_ANSWER,
    MAX_TOKENS_QUESTION,
    MAX_TOKENS_EVAL,
    TEMPERATURE_ANSWER,
    TEMPERATURE_MOCK,
    TEMPERATURE_EVAL,
)
 
load_dotenv()
 
CHAT_URL = f"{SARVAM_API_BASE}/v1/chat/completions"
 
# System Prompts
_RAG_SYSTEM = """You are an expert technical interview coach with deep knowledge
of software engineering, machine learning, data science, and behavioural interviews.
 
Rules:
- Reply in the SAME language the user asked the question in. If they asked in Tamil, answer in Tamil. If English, answer in English.
- Use ONLY the provided context to answer.
- If the context is insufficient, say so clearly — never fabricate facts.
- Be concise but thorough. Use bullet points or numbered lists where helpful.
- Include code examples when the topic is technical and a snippet adds clarity."""
 
_MOCK_SYSTEM = """You are a realistic technical interviewer conducting a mock interview.
- Ask ONE clear, well-scoped interview question matching the requested topic and level.
- Output ONLY the question itself — no preamble, no hints, no model answer."""
 
_EVAL_SYSTEM = """You are a strict but fair technical interview evaluator.
Evaluate the candidate's answer using this exact structure:
 
**Scores**
- Correctness : X / 10
- Clarity     : X / 10
- Depth       : X / 10
 
**Strengths**
(what was done well, in 2-3 bullet points)
 
**Areas for improvement**
(specific, actionable feedback in 2-3 bullet points)
 
**Model answer**
(a concise, ideal answer the interviewer would expect)"""
 
 
def _get_headers() -> dict:
    """Build headers using Sarvam auth."""
    api_key = os.environ.get("SARVAM_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError(
            "SARVAM_API_KEY is not set. Add it to your .env file. "
            "Get a free key at: https://dashboard.sarvam.ai"
        )
    return {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }
 
 
def _chat(system: str, user: str, temperature: float, max_tokens: int) -> str:
    """Send a system+user turn to Sarvam Chat and return the reply."""
    payload = {
        "model": SARVAM_CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "temperature": temperature,
        "max_tokens":  max_tokens,
    }
    try:
        resp = requests.post(CHAT_URL, headers=_get_headers(), json=payload, timeout=60)
        resp.raise_for_status()
        message = resp.json()["choices"][0]["message"]
        # sarvam-30b is a reasoning model — content can be None if max_tokens too low
        # Fall back to reasoning_content if content is empty
        content = message.get("content") or message.get("reasoning_content") or ""
        return content.strip() if content else "Error: Empty response from model. Try increasing MAX_TOKENS in config.py"
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        if status == 401:
            return "Error: Invalid Sarvam API key. Check SARVAM_API_KEY in .env"
        if status == 429:
            return "Error: Rate limit reached. Wait a moment and try again."
        return f"Error: API error {status}: {e}"
    except Exception as e:
        return f"Error: Unexpected error: {e}"
 
 
def generate_rag_answer(query: str, context_chunks: list) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No context retrieved."
    user_msg = (
        f"Context from knowledge base:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer based strictly on the context above:"
    )
    return _chat(_RAG_SYSTEM, user_msg, TEMPERATURE_ANSWER, MAX_TOKENS_ANSWER)
 
 
def generate_mock_question(topic: str) -> str:
    return _chat(
        _MOCK_SYSTEM,
        f"Give me one {topic} interview question.",
        TEMPERATURE_MOCK,
        MAX_TOKENS_QUESTION,
    )
 
 
def evaluate_answer(question: str, user_answer: str) -> str:
    user_msg = f"Interview question: {question}\n\nCandidate's answer: {user_answer}"
    return _chat(_EVAL_SYSTEM, user_msg, TEMPERATURE_EVAL, MAX_TOKENS_EVAL)
