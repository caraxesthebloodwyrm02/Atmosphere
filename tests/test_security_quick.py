import time

import pytest

from src.atmosphere_audio.core.security import APIKeyManager, JWTManager, RateLimiter


def test_jwt_access_token_roundtrip():
    manager = JWTManager()
    payload = {"username": "quick_user", "role": "user"}

    token = manager.create_access_token(payload)
    assert isinstance(token, str) and token

    token_data = manager.verify_token(token)
    assert token_data is not None
    assert token_data.username == payload["username"]
    assert token_data.role == payload["role"]


def test_api_key_generation_and_lookup(tmp_path, monkeypatch):
    storage = tmp_path / "api_keys.json"
    monkeypatch.setattr(APIKeyManager, "storage_path", str(storage), raising=False)

    manager = APIKeyManager(storage_path=str(storage))
    key = manager.generate_key(
        name="test_app", user_id="user-123", role="developer", permissions={"read"}
    )

    retrieved = manager.verify_key(key)
    assert retrieved is not None
    assert retrieved.name == "test_app"
    assert retrieved.user_id == "user-123"
    assert "read" in retrieved.permissions


def test_rate_limiter_blocks_after_threshold(monkeypatch):
    limiter = RateLimiter()
    client_id = "client-quick"

    # Use very small custom window so the test does not depend on env defaults
    assert limiter.is_allowed(client_id, max_requests=2, window_seconds=60) is True
    assert limiter.is_allowed(client_id, max_requests=2, window_seconds=60) is True
    assert limiter.is_allowed(client_id, max_requests=2, window_seconds=60) is False
    assert limiter.get_remaining_requests(client_id) == 0

    # Advance time beyond the window and ensure access is restored
    original_time = time.time
    monkeypatch.setattr(time, "time", lambda: original_time() + 120)
    try:
        assert limiter.is_allowed(client_id, max_requests=2, window_seconds=60) is True
    finally:
        monkeypatch.setattr(time, "time", original_time)
