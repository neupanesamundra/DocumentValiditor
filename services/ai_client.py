from dataclasses import dataclass
from contextlib import contextmanager
import os
import time
from typing import Optional

from config.settings import (
    AI_API_KEY,
    AI_ENABLED,
    AI_MAX_INPUT_CHARS,
    AI_MODEL,
    AI_PROVIDER,
    AI_REQUEST_TIMEOUT_SECONDS,
    AI_RETRY_ATTEMPTS,
    AI_RETRY_BACKOFF_SECONDS,
    GEMINI_API_KEY,
)

try:
    from openai import OpenAI
except ModuleNotFoundError:
    OpenAI = None

try:
    from google import genai
    from google.genai import types as genai_types
except ModuleNotFoundError:
    genai = None
    genai_types = None


@dataclass
class AIResponse:
    ok: bool
    content: str = ""
    error: str = ""
    provider: str = ""
    model: str = ""


@contextmanager
def _without_blocked_local_proxies():
    """Temporarily remove local blackhole proxy settings that break outbound AI calls."""
    proxy_keys = (
        "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
        "ALL_PROXY", "all_proxy",
    )
    blocked_hosts = {
        "http://127.0.0.1:9",
        "https://127.0.0.1:9",
        "http://localhost:9",
        "https://localhost:9",
    }
    removed = {}
    for key in proxy_keys:
        value = (os.getenv(key) or "").strip().lower()
        if value in blocked_hosts:
            removed[key] = os.environ.pop(key, None)
    try:
        yield
    finally:
        for key, value in removed.items():
            if value is not None:
                os.environ[key] = value


def _truncate_text(text: str, max_chars: Optional[int] = None) -> str:
    limit = max_chars or AI_MAX_INPUT_CHARS
    source = text or ""
    if len(source) <= limit:
        return source
    return source[:limit].rstrip()


def is_ai_available() -> bool:
    if not AI_ENABLED:
        return False
    if AI_PROVIDER == "openai":
        return bool(AI_API_KEY and OpenAI is not None)
    if AI_PROVIDER == "gemini":
        return bool((GEMINI_API_KEY or AI_API_KEY) and genai is not None and genai_types is not None)
    return False


def _is_retryable_ai_error(error_message: str) -> bool:
    lowered = (error_message or "").lower()
    retry_markers = (
        "503",
        "unavailable",
        "high demand",
        "rate limit",
        "429",
        "timeout",
        "timed out",
        "connection reset",
        "temporarily",
        "try again later",
    )
    return any(marker in lowered for marker in retry_markers)


def _friendly_ai_error_message(error_message: str) -> str:
    lowered = (error_message or "").lower()
    if any(marker in lowered for marker in ("503", "unavailable", "high demand", "try again later", "temporarily")):
        return "AI service temporarily overloaded; rule-based fallback used."
    if any(marker in lowered for marker in ("429", "rate limit")):
        return "AI request rate-limited; rule-based fallback used."
    if any(marker in lowered for marker in ("timeout", "timed out")):
        return "AI request timed out; rule-based fallback used."
    if "empty response" in lowered:
        return "AI returned an empty response; rule-based fallback used."
    return error_message or "AI request failed; rule-based fallback used."


def _request_openai_completion(system_prompt: str, user_prompt: str, temperature: float) -> AIResponse:
    with _without_blocked_local_proxies():
        client = OpenAI(api_key=AI_API_KEY, timeout=AI_REQUEST_TIMEOUT_SECONDS)
        response = client.responses.create(
            model=AI_MODEL,
            temperature=temperature,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    content = (getattr(response, "output_text", "") or "").strip()
    if not content:
        return AIResponse(
            ok=False,
            error="AI returned an empty response.",
            provider=AI_PROVIDER,
            model=AI_MODEL,
        )
    return AIResponse(
        ok=True,
        content=content,
        provider=AI_PROVIDER,
        model=AI_MODEL,
    )


def _request_gemini_completion(system_prompt: str, user_prompt: str, temperature: float) -> AIResponse:
    api_key = GEMINI_API_KEY or AI_API_KEY
    with _without_blocked_local_proxies():
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=AI_MODEL,
            contents=user_prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            ),
        )
    content = (getattr(response, "text", "") or "").strip()
    if not content:
        return AIResponse(
            ok=False,
            error="AI returned an empty response.",
            provider=AI_PROVIDER,
            model=AI_MODEL,
        )
    return AIResponse(
        ok=True,
        content=content,
        provider=AI_PROVIDER,
        model=AI_MODEL,
    )


def request_text_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_input_chars: Optional[int] = None,
) -> AIResponse:
    if not is_ai_available():
        return AIResponse(
            ok=False,
            error="AI is disabled or not configured.",
            provider=AI_PROVIDER,
            model=AI_MODEL,
        )

    truncated_user_prompt = _truncate_text(user_prompt, max_chars=max_input_chars)

    attempts = max(1, AI_RETRY_ATTEMPTS)
    last_error = ""

    for attempt in range(1, attempts + 1):
        try:
            if AI_PROVIDER == "openai":
                return _request_openai_completion(system_prompt, truncated_user_prompt, temperature)
            if AI_PROVIDER == "gemini":
                return _request_gemini_completion(system_prompt, truncated_user_prompt, temperature)
            return AIResponse(
                ok=False,
                error=f"Unsupported AI provider: {AI_PROVIDER}",
                provider=AI_PROVIDER,
                model=AI_MODEL,
            )
        except Exception as exc:
            last_error = str(exc)
            if attempt < attempts and _is_retryable_ai_error(last_error):
                time.sleep(AI_RETRY_BACKOFF_SECONDS * attempt)
                continue
            break

    return AIResponse(
        ok=False,
        error=_friendly_ai_error_message(last_error),
        provider=AI_PROVIDER,
        model=AI_MODEL,
    )
