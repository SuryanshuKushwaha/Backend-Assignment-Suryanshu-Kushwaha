import sqlite3
from datetime import datetime
from app.models import get_connection

def insert_message(data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO messages
            (message_id, from_msisdn, to_msisdn, ts, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["message_id"],
            data["from"],
            data["to"],
            data["ts"],
            data.get("text"),
            datetime.utcnow().isoformat() + "Z"
        ))
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"
    finally:
        conn.close()

def fetch_messages(limit, offset, from_, since, q):
    conn = get_connection()
    cursor = conn.cursor()

    where = []
    params = []

    if from_:
        where.append("from_msisdn = ?")
        params.append(from_)
    if since:
        where.append("ts >= ?")
        params.append(since)
    if q:
        where.append("LOWER(text) LIKE ?")
        params.append(f"%{q.lower()}%")

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    cursor.execute(f"SELECT COUNT(*) FROM messages {where_sql}", params)
    total = cursor.fetchone()[0]

    cursor.execute(f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_sql}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """, params + [limit, offset])

    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            "message_id": r[0],
            "from": r[1],
            "to": r[2],
            "ts": r[3],
            "text": r[4]
        }
        for r in rows
    ]

    return data, total

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages")
    senders = cursor.fetchone()[0]

    cursor.execute("""
        SELECT from_msisdn, COUNT(*) as c
        FROM messages
        GROUP BY from_msisdn
        ORDER BY c DESC
        LIMIT 10
    """)
    per_sender = [{"from": r[0], "count": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT MIN(ts), MAX(ts) FROM messages")
    first, last = cursor.fetchone()

    conn.close()

    return {
        "total_messages": total,
        "senders_count": senders,
        "messages_per_sender": per_sender,
        "first_message_ts": first,
        "last_message_ts": last
    }
