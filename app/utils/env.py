from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def load_env() -> None:
    """Load environment variables from the .env file once."""

    load_dotenv(override=False)


def require_env(name: str) -> str:
    """Fetch a required environment variable or raise a clear error."""

    load_env()
    value = os.getenv(name)
    if not value:
        msg = f"Missing required environment variable: {name}"
        raise RuntimeError(msg)
    return value
