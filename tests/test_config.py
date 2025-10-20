from __future__ import annotations

from pathlib import Path

import pytest

from app import config


@pytest.fixture(autouse=True)
def _clear_env_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "load_env", lambda: None)


def test_load_litellm_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_path = tmp_path / "lite.yaml"
    cfg_path.write_text(
        """
model_list:
  - model_name: local/test
    litellm_params:
      model: gpt-test
      api_key: ${API_TOKEN}
router:
  config:
    default_model: local/test
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("API_TOKEN", "secret")

    loaded = config.load_litellm_config(cfg_path)

    entry = loaded.get_model()
    assert entry.model_name == "local/test"
    assert entry.litellm_params.api_key == "secret"
    kwargs = entry.litellm_params.to_litellm_kwargs()
    assert kwargs["model"] == "gpt-test"
    assert kwargs["api_key"] == "secret"


def test_expand_env_with_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MISSING_TOKEN", raising=False)

    assert config._expand_env("${MISSING_TOKEN:-fallback}") == "fallback"
    assert config._expand_env("prefix-${MISSING_TOKEN:-fallback}") == "prefix-fallback"
