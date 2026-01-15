from fastapi.testclient import TestClient
from app.main import app
from app.storage import insert_message
client = TestClient(app)

def test_stats(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "testsecret")
    class M: pass
    m = M()
    m.message_id = "stats1"
    m.from_ = "+911111111111"
    m.to = "+12223334444"
    m.ts = "2025-01-10T09:00:00Z"
    m.text = "hello"
    insert_message(m)
    r = client.get("/stats")
    assert r.status_code == 200
    j = r.json()
    assert "total_messages" in j
