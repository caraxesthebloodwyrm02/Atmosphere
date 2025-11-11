import pytest
from fastapi.testclient import TestClient

from webui.backend.app import app, get_assistant


class FakeAssistant:
    def chat(self, messages, provider=None, model=None):
        # Echo back for deterministic testing
        user = next((m["content"] for m in messages if m.get("role") == "user"), "" )
        return f"Echo: {user}"


@pytest.fixture(autouse=True)
def override_assistant_dependency():
    # Override dependency for deterministic tests
    app.dependency_overrides[get_assistant] = lambda: FakeAssistant()
    yield
    app.dependency_overrides.clear()


def test_health_and_metrics_endpoints():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    # Hit metrics after some requests
    client.get("/health")
    m = client.get("/metrics")
    assert m.status_code == 200
    assert "requests_total" in m.text


def test_arcade_play_endpoint():
    client = TestClient(app)
    r = client.get("/arcade/play", params={"track": "demo-track"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "demo-track" in data["message"]


def test_learning_coach_endpoint_with_fake_assistant():
    client = TestClient(app)
    r = client.get("/learning/coach", params={"prompt": "help me"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["reply"].startswith("Echo:")


