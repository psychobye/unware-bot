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

from config import DFF_PATH, TEX_PATH, MAP_JSON_PATH, MAP_IDE_PATH, MESSAGE_EFFECTS
from .textures import scan_textures_by_chunks
from .names import get_name_by_id, get_model_from_ide
from .log import log_missing_dff
from .db import log_request
from .boosty import check_rate_and_alert

async def send_map_archive(bot, chat_id: int, map_id: int, retries=3, delay=1) -> bool:
    return False
