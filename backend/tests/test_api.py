import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["vector_chunks_indexed"] > 0

def test_api_analyze_text():
    res = client.post("/api/analyze/text", json={
        "text": "My tomato lower leaves have yellow rings and black spots",
        "crop": "Tomato",
        "language": "en"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert "final_result" in data
    assert "route_trace" in data

def test_api_documents_list():
    res = client.get("/api/documents/list")
    assert res.status_code == 200
    data = res.json()
    assert data["total_chunks"] >= 5

def test_api_metrics():
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_requests" in data
