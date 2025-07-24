import logging
from aiogram import types, Bot
from aiogram.types import BufferedInputFile
from .timecyc_dat import dat_to_json

logger = logging.getLogger(__name__)

async def handle_timecyc_dat(message: types.Message, bot: Bot):
    try:
        file_bytes = await bot.download(message.document)
        dat_bytes = file_bytes.read()

        json_bytes = dat_to_json(dat_bytes)

        if len(json_bytes) > 50 * 1024 * 1024:
            await message.answer("❌ размер файла слишком большой")
            return

        await message.answer_document(
            BufferedInputFile(json_bytes, filename="timecyc.json"),
            caption="✨ держи, бро, твой timecyc.json"
        )
    except Exception as e:
        logger.exception(f"timecyc dat->json error: {e}")
        await message.answer(f"❌ ошибка: {e}")
