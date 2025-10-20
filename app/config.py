from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .utils.env import load_env


class ModelParams(BaseModel):
    """Parameters passed to LiteLLM for a single backend."""

    model: str
    api_key: str | None = None
    api_base: str | None = None
    custom_llm_provider: str | None = None

    model_config = ConfigDict(extra="allow")

    def to_litellm_kwargs(self) -> dict[str, Any]:
        payload = self.model_dump(exclude_unset=True, exclude_none=True)
        payload.update(self.model_extra or {})
        return payload


class ModelEntry(BaseModel):
    """Single LiteLLM model entry."""

    model_name: str
    litellm_params: ModelParams


class RouterConfig(BaseModel):
    """Router defaults section of LiteLLM configuration."""

    default_model: str


class RouterSection(BaseModel):
    """Router wrapper containing runtime defaults."""

    config: RouterConfig


class LiteLLMConfig(BaseModel):
    """Root LiteLLM configuration."""

    model_list: list[ModelEntry]
    router: RouterSection

    def get_model(self, name: str | None = None) -> ModelEntry:
        target = name or self.router.config.default_model
        for entry in self.model_list:
            if entry.model_name == target:
                return entry
        msg = f"Unknown model '{target}'"
        raise KeyError(msg)


def load_litellm_config(path: Path | None = None) -> LiteLLMConfig:
    """Load litellm_config.yaml and resolve environment placeholders."""

    load_env()
    config_path = path or Path("litellm_config.yaml")
    raw_text = config_path.read_text()
    raw_data = yaml.safe_load(raw_text) or {}
    expanded = _expand_env(raw_data)
    try:
        return LiteLLMConfig.model_validate(expanded)
    except ValidationError as exc:  # pragma: no cover - invalid config
        raise ValueError(f"Invalid LiteLLM config: {exc}") from exc


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return _expand_string(value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(item) for item in value]
    return value


def _expand_string(value: str) -> str:
    from os import environ
    import re

    pattern = re.compile(r"\$\{([^}]+)\}")

    def substitute(match) -> str:
        spec = match.group(1)
        key = spec
        default: str | None = None

        if ":-" in spec:
            key, default = spec.split(":-", 1)
        elif "-" in spec:
            key, default = spec.split("-", 1)

        key = key.strip()
        if not key:
            return match.group(0)

        if default is not None:
            return environ.get(key, default)
        return environ.get(key, match.group(0))

    return pattern.sub(substitute, value)
