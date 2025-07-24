import aiosqlite
import time

DB_PATH = "agreement.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_agreement (
                user_id INTEGER PRIMARY KEY
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS request_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp INTEGER
            )
        """)
        await db.commit()

async def check_user_agreed(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM user_agreement WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def add_agreed_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO user_agreement (user_id) VALUES (?)", (user_id,))
        await db.commit()

async def is_rate_limited(user_id: int, period_sec: int = 3600, max_calls: int = 100) -> bool:
    now = int(time.time())
    cutoff = now - period_sec
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM request_log WHERE timestamp < ?", (cutoff,))
        async with db.execute(
            "SELECT COUNT(*) FROM request_log WHERE user_id = ? AND timestamp >= ?",
            (user_id, cutoff)
        ) as cur:
            cnt = (await cur.fetchone())[0]
        await db.commit()
    return cnt >= max_calls

async def log_request(user_id: int):
    ts = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO request_log (user_id, timestamp) VALUES (?, ?)",
            (user_id, ts)
        )
        await db.commit()
