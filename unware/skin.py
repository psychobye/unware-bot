import asyncio
import os
import random
import time
import zipfile
import time
from io import BytesIO

from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramNetworkError

from config import DFF_PATH, TEX_PATH, SKINS_IDE_PATH, SKINS_JSON_PATH, MESSAGE_EFFECTS
from .textures import scan_textures_by_chunks
from .names import get_name_by_id, get_model_from_ide
from .log import log_missing_dff
from .db import log_request
from .boosty import check_rate_and_alert

def find_file_case_insensitive(folder, filename):
    filename_lower = filename.lower()
    for f in os.listdir(folder):
        if f.lower() == filename_lower:
            return os.path.join(folder, f)
    return None

async def send_skin_archive(bot, chat_id: int, skin_id: int, retries=3, delay=1) -> bool:
    user_id = chat_id
    
    if await check_rate_and_alert(bot, user_id, chat_id):
        await bot.send_message(
            chat_id,
            "🚫 братик, ты переборщил — лимит запросов за час.\nподожди немного, потом продолжим."
        )
        return False

    await log_request(chat_id)

    model_name = get_model_from_ide(skin_id, SKINS_IDE_PATH, id_index=0, model_index=1, skip_prefixes=('#',))
    if model_name is None:
        await bot.send_message(chat_id, f"❌ не нашёл айди скина *{skin_id}* в базе, брат", parse_mode=ParseMode.MARKDOWN)
        return False

    dff_path = find_file_case_insensitive(DFF_PATH, f"{model_name}.dff")
    if dff_path is None:
        await bot.send_message(chat_id, f"🗃️ файл скина *{model_name}.dff* не найден, сори", parse_mode=ParseMode.MARKDOWN)
        log_missing_dff("skin", skin_id, model_name, bot)
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

    mem_zip.seek(0)
    model_name_fancy = get_name_by_id(skin_id, SKINS_JSON_PATH) or model_name

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            start = time.time()
            mem_zip.seek(0)
            await bot.send_document(
                chat_id=chat_id,
                document=BufferedInputFile(mem_zip.read(), filename=f"{model_name}.zip"),
                caption=f"📦 держи скин — *{model_name_fancy}* 🎨, не забудь сказать спасибо 😉",
                parse_mode=ParseMode.MARKDOWN,
                message_effect_id=random.choice(MESSAGE_EFFECTS)
            )
            return True
        except (TelegramNetworkError, asyncio.TimeoutError) as e:
            print(f'[send_skin_archive] attempt {attempt} failed: {e}, elapsed {time.time() - start:.1f} sec')
            last_exc = e
            await asyncio.sleep(delay)
        except Exception as e:
            print(f'[send_skin_archive] unknown error: {e}')
            await bot.send_message(chat_id, "❌ ошибка при отправке скина, попробуй позже")
            return False

    await bot.send_message(chat_id, "❌ ошибка сети при отправке скина, попробуй позже")
    print(f'[send_skin_archive] all {retries} attempts failed, error: {last_exc}')
    return False
