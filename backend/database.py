import aiosqlite
import os
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH", "phonedata.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS phone_numbers (
    phone_number  TEXT PRIMARY KEY,
    rating_neg    INTEGER NOT NULL DEFAULT 0,
    rating_neu    INTEGER NOT NULL DEFAULT 0,
    rating_pos    INTEGER NOT NULL DEFAULT 0,
    search_count  INTEGER NOT NULL DEFAULT 0,
    last_searched TEXT
);

CREATE TABLE IF NOT EXISTS ratings (
    phone_number  TEXT NOT NULL,
    device_id     TEXT NOT NULL,
    rating        TEXT NOT NULL CHECK(rating IN ('negative', 'neutral', 'positive')),
    created_at    TEXT NOT NULL,
    PRIMARY KEY (phone_number, device_id)
);

CREATE TABLE IF NOT EXISTS comments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number  TEXT NOT NULL,
    device_id     TEXT NOT NULL,
    text          TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_comments_phone
    ON comments(phone_number, created_at DESC);
"""


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    try:
        await db.executescript(SCHEMA)
        await db.commit()
    finally:
        await db.close()


async def lookup_number(phone_number: str) -> dict | None:
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """INSERT INTO phone_numbers (phone_number, search_count, last_searched)
               VALUES (?, 1, ?)
               ON CONFLICT(phone_number) DO UPDATE SET
                   search_count = search_count + 1,
                   last_searched = ?""",
            (phone_number, now, now),
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT * FROM phone_numbers WHERE phone_number = ?",
            (phone_number,),
        )
        row = await cursor.fetchone()
        if not row:
            return None

        comments_cursor = await db.execute(
            """SELECT text, created_at FROM comments
               WHERE phone_number = ?
               ORDER BY created_at DESC LIMIT 5""",
            (phone_number,),
        )
        comments = [
            {"text": c["text"], "created_at": c["created_at"]}
            for c in await comments_cursor.fetchall()
        ]

        neg, neu, pos = row["rating_neg"], row["rating_neu"], row["rating_pos"]
        if neg + neu + pos == 0:
            rating = "unknown"
        elif neg >= neu and neg >= pos:
            rating = "negative"
        elif pos >= neu:
            rating = "positive"
        else:
            rating = "neutral"

        return {
            "phone_number": row["phone_number"],
            "rating": rating,
            "rating_counts": {"negative": neg, "neutral": neu, "positive": pos},
            "search_count": row["search_count"],
            "comment_count": await _count_comments(db, phone_number),
            "last_searched": row["last_searched"],
            "comments": comments,
        }
    finally:
        await db.close()


async def _count_comments(db: aiosqlite.Connection, phone_number: str) -> int:
    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM comments WHERE phone_number = ?",
        (phone_number,),
    )
    row = await cursor.fetchone()
    return row["cnt"]


async def add_rating(phone_number: str, device_id: str, rating: str) -> dict:
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()

        # Ensure phone_numbers row exists
        await db.execute(
            "INSERT OR IGNORE INTO phone_numbers (phone_number) VALUES (?)",
            (phone_number,),
        )

        # Check for existing rating from this device
        cursor = await db.execute(
            "SELECT rating FROM ratings WHERE phone_number = ? AND device_id = ?",
            (phone_number, device_id),
        )
        old = await cursor.fetchone()

        if old:
            old_rating = old["rating"]
            col_map = {"negative": "rating_neg", "neutral": "rating_neu", "positive": "rating_pos"}
            await db.execute(
                f"UPDATE phone_numbers SET {col_map[old_rating]} = MAX(0, {col_map[old_rating]} - 1), "
                f"{col_map[rating]} = {col_map[rating]} + 1 WHERE phone_number = ?",
                (phone_number,),
            )
            await db.execute(
                "UPDATE ratings SET rating = ?, created_at = ? WHERE phone_number = ? AND device_id = ?",
                (rating, now, phone_number, device_id),
            )
        else:
            col_map = {"negative": "rating_neg", "neutral": "rating_neu", "positive": "rating_pos"}
            await db.execute(
                f"UPDATE phone_numbers SET {col_map[rating]} = {col_map[rating]} + 1 WHERE phone_number = ?",
                (phone_number,),
            )
            await db.execute(
                "INSERT INTO ratings (phone_number, device_id, rating, created_at) VALUES (?, ?, ?, ?)",
                (phone_number, device_id, rating, now),
            )

        await db.commit()
        return {"status": "ok", "rating": rating}
    finally:
        await db.close()


async def add_comment(phone_number: str, device_id: str, text: str) -> dict:
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()

        await db.execute(
            "INSERT OR IGNORE INTO phone_numbers (phone_number) VALUES (?)",
            (phone_number,),
        )
        await db.execute(
            "INSERT INTO comments (phone_number, device_id, text, created_at) VALUES (?, ?, ?, ?)",
            (phone_number, device_id, text, now),
        )
        await db.commit()
        return {"status": "ok", "created_at": now}
    finally:
        await db.close()


async def get_comments(phone_number: str, page: int = 1, limit: int = 20) -> dict:
    db = await get_db()
    try:
        offset = (page - 1) * limit
        total = await _count_comments(db, phone_number)

        cursor = await db.execute(
            """SELECT text, created_at FROM comments
               WHERE phone_number = ?
               ORDER BY created_at DESC LIMIT ? OFFSET ?""",
            (phone_number, limit, offset),
        )
        comments = [
            {"text": c["text"], "created_at": c["created_at"]}
            for c in await cursor.fetchall()
        ]
        return {"total": total, "page": page, "limit": limit, "comments": comments}
    finally:
        await db.close()
