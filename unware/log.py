import datetime
import asyncio
from config import ADMIN_ID, LOG_FILE

def format_log_entry(item_type: str, vehicle_id: int, model_name: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] ❌ no dff ({item_type}): id={vehicle_id}, model={model_name}"

def log_missing_dff(item_type: str, vehicle_id: int, model_name: str, bot=None):
    line = format_log_entry(item_type, vehicle_id, model_name)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    if bot:
        asyncio.create_task(send_log_to_telegram(bot, line))

def log_admin_action(text: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {text}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

async def send_log_to_telegram(bot, text: str):
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[error sending to tg] {e}\n")
