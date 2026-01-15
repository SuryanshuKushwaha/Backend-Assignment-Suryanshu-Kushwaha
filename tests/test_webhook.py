# Basic tests (not exhaustive)
from fastapi.testclient import TestClient
from app.main import app
import hmac, hashlib, json
client = TestClient(app)

def sig(body, secret):
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

def test_bad_signature(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "s")
    body = b'{"message_id":"m1","from":"+911","to":"+1","ts":"2025-01-15T10:00:00Z","text":"hi"}'
    r = client.post("/webhook", data=body, headers={"X-Signature":"bad","Content-Type":"application/json"})
    assert r.status_code == 401

def test_create_and_duplicate(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "testsecret")
    body = b'{"message_id":"mdup","from":"+911111111111","to":"+12222222222","ts":"2025-01-15T10:00:00Z","text":"hi"}'
    s = sig(body, "testsecret")
    r = client.post("/webhook", data=body, headers={"X-Signature":s,"Content-Type":"application/json"})
    assert r.status_code == 200
    r2 = client.post("/webhook", data=body, headers={"X-Signature":s,"Content-Type":"application/json"})
    assert r2.status_code == 200
