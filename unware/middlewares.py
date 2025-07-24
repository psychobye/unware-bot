import logging
from aiogram import types
from aiogram.types import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from config import ADMIN_ID
from .db import check_user_agreed
from .boosty import check_any_subscription, get_base_keyboard, get_base_message

logger = logging.getLogger(__name__)

class AgreementMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        state: FSMContext = data["state"]
        user = None

        if isinstance(event, types.Message):
            user = event.from_user
        elif isinstance(event, types.CallbackQuery):
            user = event.from_user

        if user:
            agreed_in_db = await check_user_agreed(user.id)
            user_data = await state.get_data()
            if not user_data.get("agreed") and agreed_in_db:
                await state.update_data(agreed=True)
                user_data = await state.get_data()

            if not (user_data.get("agreed") or (user.id != ADMIN_ID and agreed_in_db)):
                if isinstance(event, types.Message):
                    if not (event.text and event.text.startswith("/start")):
                        await event.answer("❌ сначала нужно принять пользовательское соглашение. набери /start")
                        return
                elif isinstance(event, types.CallbackQuery):
                    if event.data != "agree_terms":
                        await event.answer("❌ сначала нужно принять пользовательское соглашение. набери /start", show_alert=True)
                        return

        return await handler(event, data)

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        bot = data['bot']

        if isinstance(event, types.Message):
            user_id = event.from_user.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id

        if user_id == ADMIN_ID:
            return await handler(event, data)

        if user_id is not None and await check_any_subscription(bot, user_id):
            return await handler(event, data)

        kb = get_base_keyboard()
        message_text = get_base_message()

        if isinstance(event, types.Message):
            await event.reply(message_text, reply_markup=kb)
        elif isinstance(event, types.CallbackQuery):
            await event.answer("🚫 доступ только для подписчиков. проси у него 👇", show_alert=True)
            await event.message.answer("🔓 чтобы получить доступ — psychobye", reply_markup=kb)
