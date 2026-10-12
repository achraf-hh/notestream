import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_reject_an_empty_api_key(monkeypatch):
    # docker compose passes an empty string when OPENAI_API_KEY isn't set on the host.
    monkeypatch.setenv("OPENAI_API_KEY", "")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_accept_a_real_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    assert Settings(_env_file=None).openai_api_key == "sk-test"
