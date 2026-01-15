from fastapi.testclient import TestClient
from app.main import app
from app.storage import insert_message
import os
client = TestClient(app)

def test_messages_listing(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "testsecret")
    # insert a few
    class M: pass
    for i in range(3):
        m = M()
        m.message_id = f"m{i}"
        m.from_ = "+911234567890"
        m.to = "+12223334444"
        m.ts = f"2025-01-15T0{i}:00:00Z"
        m.text = "hello"
        insert_message(m)
    r = client.get("/messages")
    assert r.status_code == 200
    assert r.json()["total"] >= 3
