import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, Message
)
from aiogram.fsm.context import FSMContext
from aiogram.client.bot import DefaultBotProperties

from config import API_TOKEN, ADMIN_ID
from .db import init_db, add_agreed_user
from .car import send_car_archive
from .skin import send_skin_archive
from .mapping import send_map_archive
from .states import GetCarState, GetSkinState, GetMapState
from .mod_handlers import single_mod_handler, media_group_handler
from .dff_handlers import single_dff_handler, media_group_dff_handler
# from .btx_handlers import single_btx_handler, media_group_btx_handler
# from .png_handlers import single_png_handler, media_group_png_handler
from .bpc_handlers import handle_bpc
from .zip_handlers import handle_zip
from .timecyc_json_handlers import handle_timecyc_json
from .timecyc_dat_handlers import handle_timecyc_dat
from .middlewares import SubscriptionMiddleware, AgreementMiddleware
from .boosty import check_pro_subscription, get_pro_keyboard, get_pro_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# define tab and action buttons
tab_buttons = ["модельки", "конвертация"]
model_buttons = [
    ("🚗 машина", "getcar_start"),
    ("🎨 скин", "getskin_start"),
    ("🗺️ маппинг", "getmapping_start"),
]
convert_buttons = [
    ("🧙‍♂️ .mod → .dff", "mod_convert"),
    ("🦝 .btx → .png", "btx_convert"),
    ("🍩 .bpc → .zip", "bpc_convert"),
    ("🦄 timecyc.json → .dat", "timecyc_convert"),
]

router = Router()

# reply keyboard
def make_reply_tab(active_tab: str) -> ReplyKeyboardMarkup:
    buttons = model_buttons if active_tab == "модельки" else convert_buttons
    keyboard = []

    tab_row = [
        KeyboardButton(text=(f"» {t} «" if t == active_tab else t))
        for t in tab_buttons
    ]
    keyboard.append(tab_row)

    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(text=buttons[j][0]) for j in range(i, min(i+2, len(buttons)))]
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# inline keyboard
def make_inline_tab(active_tab: str) -> InlineKeyboardMarkup:
    buttons = model_buttons if active_tab == "модельки" else convert_buttons
    inline_keyboard = []

    tab_row = [
        InlineKeyboardButton(text=(f"» {t} «" if t == active_tab else t), callback_data=f"tab_{t}")
        for t in tab_buttons
    ]
    inline_keyboard.append(tab_row)

    for i in range(0, len(buttons), 2):
        row = [InlineKeyboardButton(text=buttons[j][0], callback_data=buttons[j][1]) for j in range(i, min(i+2, len(buttons)))]
        inline_keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

@router.message(Command('start'))
@router.message(lambda m: m.text and m.text.startswith('/start '))
async def start(message: Message, state: FSMContext):
    print(f'[start] from {message.from_user.id} ({message.from_user.username}): {message.text}')
    data = await state.get_data()
    print(f'[start] state data: {data}')

    if not data.get('agreed'):
        print('[start] user has not agreed — sending agreement')
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ согласен', callback_data='agree_terms')],
            [InlineKeyboardButton(text='📖 документация', url='https://teletype.in/@psychobye/document')]
        ])
        await message.answer(
            "🚫 *пользовательское соглашение*\n\n"
            "📦 все модели, что выдаёт бот — только для личного использования.\n"
            "❌ распространение архивов — строго запрещено.\n"
            "👊 за нарушение — бан и отмена подписки.\n\n"
            "чтобы работать с ботом, нужно принять соглашение — жми 'согласен' 👇\n\n"
            "❓ вся инфа про бота и как им пользоваться — в нашей документации, не пропусти:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb
        )
        return

    args = message.text.split(' ', 1)
    deep = args[1] if len(args) > 1 else None
    print(f'[start] deeplink param: {deep}')

    if deep and deep.startswith("get_car_"):
        cid = deep.removeprefix("get_car_")
        print(f'[start] processing get_car with id={cid}')
        if cid.isdigit():
            await state.set_state(GetCarState.waiting_for_car_id)
            fake = message.model_copy(update={"text": cid})
            try:
                await process_car_id(fake, state)
            except Exception as e:
                print(f'[start] error in process_car_id: {e}')
                await message.answer('❌ ошибка при обработке тачки, попробуй позже')
        return

    elif deep and deep.startswith("get_skin_"):
        sid = deep.removeprefix("get_skin_")
        print(f'[start] processing get_skin with id={sid}')
        if sid.isdigit():
            await state.set_state(GetSkinState.waiting_for_skin_id)
            fake = message.model_copy(update={"text": sid})
            try:
                await process_skin_id(fake, state)
            except Exception as e:
                print(f'[start] error in process_skin_id: {e}')
                await message.answer('❌ ошибка при обработке скина, попробуй позже')
        return
    
    elif deep and deep.startswith("get_map_"):
        mid = deep.removeprefix("get_map_")
        print(f'[start] processing get_map with id={mid}')
        if mid.isdigit():
            if not await check_pro_subscription(message.bot, message.from_user.id):
                await message.answer(get_pro_message(), reply_markup=get_pro_keyboard())
                return
            await state.set_state(GetMapState.waiting_for_map_id)
            fake = message.model_copy(update={"text": mid})
            try:
                await process_map_id(fake, state)
            except Exception as e:
                print(f'[start] error in process_map_id: {e}')
                await message.answer('❌ ошибка при обработке маппинга, попробуй позже')
        return

    print('[start] sending greeting and default menu')
    reply_kb = make_reply_tab("модельки")
    inline_kb = make_inline_tab("модельки")
    await message.answer(
        f"йо, *{message.from_user.first_name or 'братик'}!* 👋\n"
        "я шарю, зачем ты тут. тебе нужны модельки — я их раздаю 🎁\n"
        "жми на кнопку ниже или снизу под сообщением\n\n"
        "айди + выбор тачки тут:\n"
        "[🔗 miniapp](https://unware.ru)\n\n"
        "_база регулярно пополняется, не теряйся_ 👀",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_kb
    )
    await message.answer('выбирай, братик, что надо 👇', reply_markup=inline_kb)

@router.callback_query(F.data == "agree_terms")
async def agree_terms(cb: CallbackQuery, state: FSMContext):
    await add_agreed_user(cb.from_user.id)
    await state.update_data(agreed=True)
    await cb.message.delete()
    await cb.answer('добро пожаловать 🤝')
    await start(cb.message, state)

# switch tabs via reply keyboard
@router.message(F.text.in_(tab_buttons))
async def switch_tab(m: Message, state: FSMContext):
    tab = m.text
    reply_kb = make_reply_tab(tab)
    await m.answer(f"открываем вкладку '{tab}'👇", reply_markup=reply_kb)

# switch tabs via inline buttons
@router.callback_query(F.data.startswith('tab_'))
async def switch_tab_inline(c: CallbackQuery):
    tab = c.data.split('_', 1)[1]
    inline_kb = make_inline_tab(tab)

    await c.message.edit_reply_markup(reply_markup=inline_kb)
    await c.answer()

# reply handlers for model actions
@router.message(F.text.in_([b[0] for b in model_buttons]))
async def reply_models(m: Message, state: FSMContext):
    text = m.text
    if text == model_buttons[0][0]:
        await m.answer('введи айди машины 😎')
        await state.set_state(GetCarState.waiting_for_car_id)
    elif text == model_buttons[1][0]:
        await m.answer('введи айди скина 🎨')
        await state.set_state(GetSkinState.waiting_for_skin_id)
    else:
        if not await check_pro_subscription(m.bot, m.from_user.id):
            return await m.answer(get_pro_message(), reply_markup=get_pro_keyboard())
        await m.answer('введи айди маппинга 🗺️')
        await state.set_state(GetMapState.waiting_for_map_id)

# reply handlers for conversion actions
@router.message(F.text.in_([b[0] for b in convert_buttons]))
async def reply_converts(m: Message):
    mapping = {
        convert_buttons[0][0]: 'сбрасывай .mod 🔮',
        convert_buttons[1][0]: 'кидай .btx 🖼️',
        convert_buttons[2][0]: 'закидывай .bpc 📦',
        convert_buttons[3][0]: 'давай .json 🚀',
    }
    await m.answer(mapping[m.text])

# inline handlers for model actions
@router.callback_query(F.data.in_([d for _,d in model_buttons]))
async def inline_models(c: CallbackQuery, state: FSMContext):
    d = c.data
    if d == 'getcar_start':
        await c.message.answer('введи айди машины 😎')
        await state.set_state(GetCarState.waiting_for_car_id)
    elif d == 'getskin_start':
        await c.message.answer('введи айди скина 🎨')
        await state.set_state(GetSkinState.waiting_for_skin_id)
    else:
        if not await check_pro_subscription(c.bot, c.from_user.id):
            await c.answer('🚫 PRO нужен', show_alert=True)
            return await c.message.answer(get_pro_message(), reply_markup=get_pro_keyboard())
        await c.message.answer('введи айди маппинга 🗺️')
        await state.set_state(GetMapState.waiting_for_map_id)
    await c.answer()

# inline handlers for conversion actions
@router.callback_query(F.data.in_([d for _,d in convert_buttons]))
async def inline_converts(c: CallbackQuery):
    text = {
        'mod_convert':'сбрасывай .mod 🔮',
        'btx_convert':'кидай .btx 🖼️',
        'bpc_convert':'закидывай .bpc 📦',
        'timecyc_convert':'давай .json 🚀'
    }[c.data]
    await c.message.answer(text)
    await c.answer()

# states
@router.message(GetCarState.waiting_for_car_id)
async def process_car_id(m: Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer('❌ айди число')
    await send_car_archive(m.bot, m.chat.id, int(m.text))
    data = await state.get_data()
    await state.clear()
    if data.get('agreed'):
        await state.update_data(agreed=True)

@router.message(GetSkinState.waiting_for_skin_id)
async def process_skin_id(m: Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer('❌ айди число')
    await send_skin_archive(m.bot, m.chat.id, int(m.text))
    data = await state.get_data()
    await state.clear()
    if data.get('agreed'):
        await state.update_data(agreed=True)

@router.message(GetMapState.waiting_for_map_id)
async def process_map_id(m: Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer('❌ айди число')
    await send_map_archive(m.bot, m.chat.id, int(m.text))
    data = await state.get_data()
    await state.clear()
    if data.get('agreed'):
        await state.update_data(agreed=True)

# file handlers
# -- single file handlers
exts_single = {
    '.mod': single_mod_handler,
    '.dff': single_dff_handler,
    #'.btx': single_btx_handler,
    #'.png': single_png_handler,
    '.bpc': handle_bpc,
    '.zip': handle_zip,
    '.json': handle_timecyc_json,
    '.dat': handle_timecyc_dat,
}
for ext, handler in exts_single.items():
    router.message(lambda m, e=ext: m.document and m.document.file_name.endswith(e) and not m.media_group_id)(handler)

# -- media group handlers
exts_media_group = {
    '.mod': media_group_handler,
    '.dff': media_group_dff_handler,
    #'.btx': media_group_btx_handler,
    #'.png': media_group_png_handler,
}
for ext, handler in exts_media_group.items():
    router.message(lambda m, e=ext: m.document and m.document.file_name.endswith(e) and m.media_group_id is not None)(handler)

async def main():
    await init_db()
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())
    dp.message.middleware(AgreementMiddleware())
    dp.callback_query.middleware(AgreementMiddleware())
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
