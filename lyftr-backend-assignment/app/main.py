import hmac
import hashlib
import uuid
import time
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from app.config import WEBHOOK_SECRET
from app.models import init_db
from app.storage import insert_message, fetch_messages, get_stats
from app.logging_utils import log
from app.metrics import inc_http, inc_webhook, render_metrics


app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

class WebhookPayload(BaseModel):
    message_id: str = Field(min_length=1)
    from_: str = Field(alias="from", pattern=r"^\+\d+$")
    to: str = Field(pattern=r"^\+\d+$")

    ts: str
    text: str | None = Field(default=None, max_length=4096)

def verify_signature(secret: str, body: bytes, signature: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/webhook")
async def webhook(request: Request):
    start = time.time()
    req_id = str(uuid.uuid4())

    body = await request.body()
    sig = request.headers.get("X-Signature")

    if not sig or not verify_signature(WEBHOOK_SECRET, body, sig):
        inc_webhook("invalid_signature")
        inc_http("/webhook", 401)
        log({
            "level": "ERROR",
            "request_id": req_id,
            "method": "POST",
            "path": "/webhook",
            "status": 401,
            "latency_ms": 0,
            "result": "invalid_signature"
        })
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = WebhookPayload.model_validate_json(body)

    result = insert_message(payload.model_dump(by_alias=True))
    inc_webhook(result)
    inc_http("/webhook", 200)

    log({
        "level": "INFO",
        "request_id": req_id,
        "method": "POST",
        "path": "/webhook",
        "status": 200,
        "latency_ms": int((time.time() - start) * 1000),
        "message_id": payload.message_id,
        "dup": result == "duplicate",
        "result": result
    })

    return {"status": "ok"}

@app.get("/messages")
def messages(limit: int = 50, offset: int = 0, from_: str | None = None, since: str | None = None, q: str | None = None):
    data, total = fetch_messages(limit, offset, from_, since, q)
    inc_http("/messages", 200)
    return {"data": data, "total": total, "limit": limit, "offset": offset}

@app.get("/stats")
def stats():
    inc_http("/stats", 200)
    return get_stats()

@app.get("/health/live")
def live():
    return {"status": "alive"}

@app.get("/health/ready")
def ready():
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=503)
    return {"status": "ready"}

@app.get("/metrics")
def metrics():
    return render_metrics()
