import aiosqlite
import os

DB_PATH = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                city TEXT,
                subscribed INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                photo_id TEXT,
                voice_id TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                remind_at TEXT,
                sent INTEGER DEFAULT 0
            )
        """)
        await db.commit()

# ─── USERS ───────────────────────────────────────────

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def save_user(user_id: int, city: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, city) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET city = COALESCE(?, city)
        """, (user_id, city, city))
        await db.commit()

async def set_subscription(user_id: int, status: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, subscribed) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET subscribed = ?
        """, (user_id, int(status), int(status)))
        await db.commit()

async def get_subscribers():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id, city FROM users WHERE subscribed = 1") as cursor:
            return await cursor.fetchall()

# ─── NOTES ───────────────────────────────────────────

async def add_note(user_id: int, text: str = None, photo_id: str = None, voice_id: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO notes (user_id, text, photo_id, voice_id) VALUES (?, ?, ?, ?)",
            (user_id, text, photo_id, voice_id)
        )
        await db.commit()

async def get_notes(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, text, photo_id, voice_id, created_at FROM notes WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()

async def delete_note(user_id: int, note_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
        await db.commit()

# ─── REMINDERS ───────────────────────────────────────

async def add_reminder(user_id: int, text: str, remind_at: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reminders (user_id, text, remind_at) VALUES (?, ?, ?)",
            (user_id, text, remind_at)
        )
        await db.commit()

async def get_pending_reminders():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, user_id, text FROM reminders
            WHERE sent = 0 AND remind_at <= datetime('now')
        """) as cursor:
            return await cursor.fetchall()

async def mark_reminder_sent(reminder_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))
        await db.commit()
