import asyncio
import logging
import traceback
import time

from aiogram import Bot, types
from aiogram.types import BufferedInputFile

from .boosty import get_user_limits
from .zip import async_convert_and_save_zip

logger = logging.getLogger(__name__)

zip_user_cooldowns = {}

async def handle_zip(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    limits = await get_user_limits(bot, user_id)
    logger.info(f"single .zip from user {user_id}")

    now = time.monotonic()
    last = zip_user_cooldowns.get(user_id, 0)
    if now - last < limits["COOLDOWN"]:
        wait = limits["COOLDOWN"] - (now - last)
        logger.warning(f"user cooldown: wait {wait:.1f} sec")
        await message.answer(f"⏳ стой, подожди {wait:.1f} сек")
        return
    zip_user_cooldowns[user_id] = now

    try:
        file_bytes = await bot.download(message.document)
        zip_bytes = file_bytes.read()

        bpc_data, bpc_name = await async_convert_and_save_zip(zip_bytes, message.document.file_name)
        logger.info(f"converted: {message.document.file_name} -> {bpc_name}")

        if len(bpc_data) > 50 * 1024 * 1024:
            logger.error("converted file too big")
            await message.answer("❌ размер файла слишком большой, не могу обработать")
            return

        await message.answer_document(
            BufferedInputFile(bpc_data, filename=bpc_name),
            caption="✨ твой файл закодирован и готов к бою! 🔐"
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"conversion error: {e.__class__.__name__}: {e}\n{tb}")
        await message.answer(f"❌ ошибка при конверте: {e.__class__.__name__}: {e}")
