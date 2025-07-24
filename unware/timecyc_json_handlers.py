import logging
import traceback
from aiogram import types, Bot
from aiogram.types import BufferedInputFile
from .timecyc_json import json_to_dat

logger = logging.getLogger(__name__)

async def handle_timecyc_json(message: types.Message, bot: Bot):
    try:
        file_bytes = await bot.download(message.document)
        json_bytes = file_bytes.read()

        dat_bytes = json_to_dat(json_bytes)

        if len(dat_bytes) > 50 * 1024 * 1024:
            await message.answer("❌ размер файла слишком большой")
            return

        await message.answer_document(
            BufferedInputFile(dat_bytes, filename="timecyc.dat"),
            caption="✨ держи, бро, твой timecyc.dat"
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"timecyc json->dat error: {e.__class__.__name__}: {e}\n{tb}")
        await message.answer(f"❌ ошибка: {e.__class__.__name__}: {e}")
