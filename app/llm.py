from __future__ import annotations

import os
from functools import lru_cache

from openai import AsyncOpenAI

from .utils.env import load_env

DEFAULT_PROXY_URL = "http://localhost:4000/v1"
DEFAULT_PROXY_KEY = "proxy-token"


@lru_cache(maxsize=1)
def get_async_client() -> AsyncOpenAI:
    """Return a cached AsyncOpenAI client configured for the LiteLLM proxy."""

    load_env()
    base_url = os.getenv("LITELLM_PROXY_URL", DEFAULT_PROXY_URL).rstrip("/")
    # openai SDK expects base_url without trailing slash and appends /chat/...
    api_key = os.getenv("LITELLM_PROXY_API_KEY", DEFAULT_PROXY_KEY)
    return AsyncOpenAI(api_key=api_key, base_url=base_url)
