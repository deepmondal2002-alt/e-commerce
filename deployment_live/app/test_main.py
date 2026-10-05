import os

os.environ.setdefault("TEST_MODE", "true")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_payload_shape():
    payload = client.get("/health").json()
    assert payload["status"] == "healthy"
    assert "rag_ready" in payload
    assert "test_mode" in payload


def test_health_reports_test_mode():
    assert client.get("/health").json()["test_mode"] is True


def test_ask_rejected_when_rag_not_ready():
    response = client.post("/ask", json={"question": "How much annual leave?"})
    assert response.status_code == 503