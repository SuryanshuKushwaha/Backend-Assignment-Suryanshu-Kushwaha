# Lyftr AI - Backend Assignment (FastAPI)

Implementation of the assignment requirements (webhook ingestion, signature, health, messages, stats, metrics).

## Run (local / docker)
Set environment variables:
```
export WEBHOOK_SECRET="testsecret"
export DATABASE_URL="sqlite:////data/app.db"
make up
```
Health:
- http://localhost:8000/health/live
- http://localhost:8000/health/ready

Webhook:
POST /webhook with JSON body and header `X-Signature` set to hex HMAC-SHA256 of raw body using WEBHOOK_SECRET.

Messages:
GET /messages?limit=50&offset=0

Stats:
GET /stats

Metrics (text):
GET /metrics

## Design notes
- HMAC verification: hex-encoded HMAC-SHA256 over raw request body using WEBHOOK_SECRET (see app/main.py).
- Pagination: limit (1-100) and offset; default ordering `ORDER BY ts ASC, message_id ASC`.
- Idempotency enforced by PRIMARY KEY on `message_id`.
- Logs: one JSON-line per request produced by middleware and additional webhook logs include `message_id`, `dup`, `result`.
- DB: SQLite file stored at `/data/app.db` via Docker volume.

## Setup Used
VSCode + Copilot + occasional ChatGPT prompts
