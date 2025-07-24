import os
import random
from time import time
import zipfile
from io import BytesIO
import asyncio
import time

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramNetworkError

from config import DFF_PATH, TEX_PATH, CARS_JSON_PATH, CARS_IDE_PATH, MESSAGE_EFFECTS
from .textures import scan_textures_by_chunks
from .names import get_name_by_id, get_model_from_ide
from .log import log_missing_dff
from .db import log_request
from .boosty import check_rate_and_alert

async def send_car_archive(bot, chat_id: int, vehicle_id: int, retries=3, delay=1) -> bool:
    user_id = chat_id
    
    try:
        if await check_rate_and_alert(bot, user_id, chat_id):
            await bot.send_message(chat_id, "🚫 братик, ты переборщил — лимит запросов за час.\nподожди немного, потом продолжим.")
            return False
    except Exception as e:
        print(f'[send_car_archive] ошибка в check_rate_and_alert: {e}')

    try:
        await log_request(chat_id)
    except Exception as e:
        print(f'[send_car_archive] ошибка в log_request: {e}')

    model_name = get_model_from_ide(vehicle_id, CARS_IDE_PATH, id_index=0, model_index=1, skip_prefixes=('#', 'cars'))
    if model_name is None:
        await bot.send_message(chat_id, f"❌ не нашёл айди *{vehicle_id}* в базе, брат", parse_mode=ParseMode.MARKDOWN)
        return False

    dff_path = os.path.join(DFF_PATH, f"{model_name}.dff")
    if not os.path.exists(dff_path):
        await bot.send_message(chat_id, f"🗃️ файл *{model_name}.dff* не найден, сори", parse_mode=ParseMode.MARKDOWN)
        log_missing_dff("car", vehicle_id, model_name, bot)
        return False

    textures = scan_textures_by_chunks(dff_path)
    textures = list(dict.fromkeys(textures))

    mem_zip = BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(dff_path, arcname=f"{model_name}.dff")
        for tex in textures:
            for ext in ['.png', '.jpg', '.bmp', '.dds']:
                tex_file = os.path.join(TEX_PATH, f"{tex}{ext}")
                if os.path.exists(tex_file):
                    arcname = os.path.join("tex", f"{tex}{ext}")
                    zipf.write(tex_file, arcname=arcname)
                    break

    model_name_fancy = get_name_by_id(vehicle_id, CARS_JSON_PATH) or model_name

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            start = time.time()
            mem_zip.seek(0) 
            await bot.send_document(
                chat_id=chat_id,
                document=BufferedInputFile(mem_zip.read(), filename=f"{model_name}.zip"),
                caption=f"📦 держи своё добро — *{model_name_fancy}* 🚗, не забудь сказать спасибо 😉",
                parse_mode=ParseMode.MARKDOWN,
                message_effect_id=random.choice(MESSAGE_EFFECTS)
            )
            return True
        except (TelegramNetworkError, asyncio.TimeoutError) as e:
            print(f'[send_car_archive] попытка {attempt} ошибка: {e}, прошло {time.time() - start:.1f} сек')
            last_exc = e
            await asyncio.sleep(delay)
        except Exception as e:
            print(f'[send_car_archive] неизвестная ошибка: {e}')
            await bot.send_message(chat_id, "❌ ошибка при отправке тачки, попробуй позже")
            return False

    await bot.send_message(chat_id, "❌ ошибка сети при отправке тачки, попробуй позже")
    print(f'[send_car_archive] все {retries} попыток неудачны, ошибка: {last_exc}')
    return False
