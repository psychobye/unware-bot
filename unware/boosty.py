import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .db import is_rate_limited

from config import (
    ADMIN_ID,
    CHAT_ID,
    PRO_CHAT_ID,
    BOOSTY_URL,
    BOOSTY_PRO_URL,
    BASE_LIMITS,
    PRO_LIMITS
)

logger = logging.getLogger(__name__)

async def check_base_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHAT_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Base subscription check error: {e}")
        return False

async def check_pro_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(PRO_CHAT_ID, user_id)
        return member.status not in ['left', 'kicked', 'restricted']
    except Exception as e:
        logger.error(f"PRO subscription check error: {e}")
        return False

async def check_any_subscription(bot: Bot, user_id: int) -> bool:
    return await check_base_subscription(bot, user_id) or await check_pro_subscription(bot, user_id)

def get_base_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 получить доступ", url=BOOSTY_URL)]
    ])

def get_pro_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔒 подписаться на Boosty Pro", url=BOOSTY_PRO_URL)]
    ])

def get_base_message() -> str:
    return (
        "🚫 доступ открыт только для сабов.\n"
        "оформи подписку на Boosty, чтоб ворваться 👉"
    )

def get_pro_message() -> str:
    return (
        "🚫 доступ открыт только для PRO сабов.\n"
        "оформи подписку на Boosty, чтоб ворваться 👉"
    )

async def get_user_limits(bot, user_id: int) -> dict:
    if await check_pro_subscription(bot, user_id):
        logger.info(f"🔥 user {user_id} — PRO")
        return PRO_LIMITS
    elif await check_base_subscription(bot, user_id):
        logger.info(f"⭐ user {user_id} — BASE")
        return BASE_LIMITS
    
async def alert_admin_on_spam(bot, user_id: int, chat_id: int):
    try:
        user = await bot.get_chat(user_id)
        name = user.full_name or "неизвестно"
        username = f"@{user.username}" if user.username else "без юзернейма"
        msg = (f"⚠️ юзер {user_id} превысил лимит запросов!\n"
               f"имя: {name}\n"
               f"юзернейм: {username}")
        await bot.send_message(ADMIN_ID, msg)
    except Exception as e:
        await bot.send_message(ADMIN_ID, f"⚠️ юзер {user_id}, не удалось получить инфу: {e}")

async def check_rate_and_alert(bot, user_id: int, chat_id: int):
    if user_id == ADMIN_ID:
        return False

    if await is_rate_limited(user_id, period_sec=3600, max_calls=50):
        await alert_admin_on_spam(bot, user_id, chat_id)
        return True
    return False
