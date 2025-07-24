import traceback
import logging
import time

from aiogram import Bot, types
from aiogram.types import BufferedInputFile

from .boosty import get_user_limits
from .bpc import async_convert_and_save_bpc

logger = logging.getLogger(__name__)

bpc_user_cooldowns = {}

async def handle_bpc(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    limits = await get_user_limits(bot, user_id)
    logger.info(f"single .bpc from user {user_id}")

    now = time.monotonic()
    last = bpc_user_cooldowns.get(user_id, 0)
    if now - last < limits["COOLDOWN"]:
        wait = limits["COOLDOWN"] - (now - last)
        logger.warning(f"user cooldown: wait {wait:.1f} sec")
        await message.answer(f"⏳ погоди чутка, жди {wait:.1f} сек")
        return
    bpc_user_cooldowns[user_id] = now

    try:
        file_bytes = await bot.download(message.document)
        bpc_bytes = file_bytes.read()

        zip_data, zip_name = await async_convert_and_save_bpc(bpc_bytes, message.document.file_name)
        logger.info(f"converted: {message.document.file_name} -> {zip_name}")

        if len(zip_data) > 50 * 1024 * 1024:
            logger.error("converted file too big")
            await message.answer("❌ размер файла больше 50 МБ, я не потяну")
            return

        await message.answer_document(
            BufferedInputFile(zip_data, filename=zip_name),
            caption="✨ расшифровочка в кармане, юзай без тормозов!"
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"conversion error: {e.__class__.__name__}: {e}\n{tb}")
        await message.answer(f"❌ ошибка при конверте: {e.__class__.__name__}: {e}")
