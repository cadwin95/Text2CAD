from __future__ import annotations

import os
import time
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

import pytest
from openai import OpenAI


PROXY_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000/v1").rstrip("/")
PROXY_API_KEY = os.getenv("LITELLM_PROXY_API_KEY", "proxy-token")
DEFAULT_TIMEOUT = float(os.getenv("LITELLM_PROXY_TEST_TIMEOUT", "30"))


def _wait_for_proxy() -> None:
    models_url = f"{PROXY_URL}/models"
    deadline = time.time() + 5
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            request = Request(models_url, method="GET")
            with urlopen(request, timeout=1):
                return
        except HTTPError as exc:  # pragma: no cover - proxy errors
            if exc.code in {401, 403}:
                return
            last_error = exc
            time.sleep(0.25)
        except URLError as exc:
            last_error = exc
            time.sleep(0.25)

    if last_error:
        pytest.skip(f"LiteLLM proxy unavailable: {last_error}")
    else:  # pragma: no cover - unexpected fallthrough
        pytest.skip("LiteLLM proxy unavailable")


def _make_client() -> OpenAI:
    return OpenAI(api_key=PROXY_API_KEY, base_url=PROXY_URL)


def _call_completion(model: str, prompt: str) -> str:
    client = _make_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return concise text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=64,
            temperature=0,
            timeout=DEFAULT_TIMEOUT,
        )
    except Exception as exc:  # pragma: no cover - network issues
        pytest.skip(f"Skipping proxy test for {model}: {exc}")

    choice = response.choices[0]
    content = (choice.message.content or "").strip()
    if not content:
        pytest.fail(f"Empty response from model {model}")
    return content


def _require_env(name: str) -> None:
    if not os.getenv(name):
        pytest.skip(f"{name} is not set; skipping")


@pytest.mark.integration
def test_proxy_completion_openai() -> None:
    _require_env("OPENAI_API_KEY")
    _wait_for_proxy()
    result = _call_completion("openai/gpt-4o-mini", "Respond with the word OPENAI.")
    assert "openai" in result.lower()


@pytest.mark.integration
def test_proxy_completion_groq() -> None:
    _require_env("GROQ_API_KEY")
    _wait_for_proxy()
    result = _call_completion("groq/gpt-oss-20b", "State GROQ in uppercase once.")
    assert "GROQ" in result


@pytest.mark.integration
def test_proxy_completion_llamacpp() -> None:
    _wait_for_proxy()
    result = _call_completion("llama.cpp", "Reply with llama once.")
    assert "llama" in result.lower()
