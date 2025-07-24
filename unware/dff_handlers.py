import asyncio
import traceback
import time
import io
import logging
import os
import zipfile

from aiogram import Bot, types
from aiogram.types import BufferedInputFile

from .boosty import get_user_limits

logger = logging.getLogger(__name__)

dff_media_groups = {}
dff_processing_tasks = {}
dff_user_cooldowns = {}
dff_cooldown_blocked_groups = {}

async def process_dff_media_group(user_id: int, group_id: str, generation: int, chat_id: int, bot: Bot):
    limits = await get_user_limits(bot, user_id)
    group_data = None
    try:
        await asyncio.sleep(limits["GROUP_PROCESSING_DELAY"])
        
        if (user_id not in dff_media_groups or 
            group_id not in dff_media_groups[user_id] or
            dff_media_groups[user_id][group_id]['generation'] != generation):
            logger.info(f"skipping outdated task for DFF group {group_id}")
            return
            
        group_data = dff_media_groups[user_id][group_id]
        docs = group_data['docs']
        
        filenames = [doc.file_name for doc in docs]
        if len(filenames) != len(set(filenames)):
            await bot.send_message(chat_id, "❌ в группе есть файлы с одинаковыми именами. плиз, переименуй файлы и отправь.")
            logger.error(f"duplicate filenames in DFF group {group_id}: {filenames}")
            return

        semaphore = asyncio.Semaphore(limits["MAX_CONCURRENT_CONVERSIONS"])
        
        async def process_dff(doc):
            async with semaphore:
                try:
                    file_bytes = await bot.download(doc)
                    dff_data = file_bytes.read()
                    # меняем расширение на .mod
                    mod_filename = os.path.splitext(doc.file_name)[0] + '.mod'
                    return (True, doc.file_name, mod_filename, dff_data, None)
                except Exception as e:
                    return (False, doc.file_name, None, None, str(e))
        
        tasks = [process_dff(doc) for doc in docs]
        results = await asyncio.gather(*tasks)
        
        out_io = io.BytesIO()
        success_count = 0
        errors = []
        used_names = {}
        
        with zipfile.ZipFile(out_io, 'w') as zout:
            for status, filename, mod_filename, dff_data, error in results:
                if not status:
                    errors.append(f"❌ {filename}: {error}")
                    continue
                
                archive_name = mod_filename
                base_name, ext = os.path.splitext(mod_filename)
                counter = 1
                while archive_name in used_names:
                    archive_name = f"{base_name}_{counter}{ext}"
                    counter += 1
                used_names[archive_name] = True
                
                zout.writestr(archive_name, dff_data)
                success_count += 1
                logger.info(f"renamed DFF: {filename} -> {archive_name}")

        if success_count == 0:
            await bot.send_message(chat_id, "⚠️ не удалось обработать ни один файл:\n" + "\n".join(errors))
            return

        archive_size = out_io.tell()
        if archive_size > limits["MAX_ARCHIVE_SIZE"]:
            await bot.send_message(chat_id, "❌ размер архива превышает лимит (20 МБ)")
            return
            
        out_io.seek(0)
        caption = f"✨ держи свои файлы, чемпион!"
        if errors:
            caption += "\nошибки:\n" + "\n".join(errors)
        
        if group_data and group_data.get('processing_msg'):
            try:
                await bot.delete_message(chat_id, group_data['processing_msg'])
            except Exception as e:
                logger.error(f"failed to delete indicator: {str(e)}")
        
        await bot.send_document(
            chat_id,
            BufferedInputFile(out_io.getvalue(), filename="mod.zip"),
            caption=caption
        )
        logger.info(f"sent DFF archive for group {group_id}")

    except asyncio.CancelledError:
        logger.info(f"DFF processing cancelled for group {group_id}")
    except Exception as e:
        logger.exception(f"critical error in DFF group processing: {str(e)}")
        await bot.send_message(chat_id, f"❌ системная ошибка: {str(e)}")
    finally:
        if group_data and group_data.get('processing_msg'):
            try:
                await bot.delete_message(chat_id, group_data['processing_msg'])
            except:
                pass
        
        if user_id in dff_media_groups and group_id in dff_media_groups[user_id]:
            del dff_media_groups[user_id][group_id]
            if not dff_media_groups[user_id]:
                del dff_media_groups[user_id]
                
        task_key = (user_id, group_id)
        if task_key in dff_processing_tasks:
            del dff_processing_tasks[task_key]

async def single_dff_handler(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    limits = await get_user_limits(bot, user_id)
    logger.info(f"single .dff file from user {user_id}")
    
    now = time.monotonic()
    last = dff_user_cooldowns.get(user_id, 0)
    if now - last < limits["COOLDOWN"] :
        wait = limits["COOLDOWN"] - (now - last)
        logger.warning(f"user {user_id} is on DFF cooldown , wait {wait:.1f} sec")
        await message.answer(f"⏳ куда спешим?! жди {wait:.1f} сек")
        return
    dff_user_cooldowns[user_id] = now

    try:
        file_bytes = await bot.download(message.document)
        dff_data = file_bytes.read()
        
        mod_filename = os.path.splitext(message.document.file_name)[0] + '.mod'

        if len(dff_data) > 50 * 1024 * 1024:
            logger.error(f"file too big: {len(dff_data)} bytes")
            await message.answer("❌ размер файла превышает 50 МБ")
            return
            
        await message.answer_document(
            BufferedInputFile(dff_data, filename=mod_filename), 
            caption="✨ держи, братик :3"
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception(f"DFF handling error: {e.__class__.__name__}: {e}\n{tb}")
        await message.answer(f"❌ ошибка: {e.__class__.__name__}: {e}")

async def media_group_dff_handler(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    group_id = message.media_group_id
    limits = await get_user_limits(bot, user_id)
    
    if user_id in dff_cooldown_blocked_groups and group_id in dff_cooldown_blocked_groups[user_id]:
        return
    
    if user_id not in dff_media_groups:
        dff_media_groups[user_id] = {}
    
    is_new_group = False
    if group_id not in dff_media_groups[user_id]:
        is_new_group = True
        
        now = time.monotonic()
        last_request = dff_user_cooldowns.get(user_id, 0)
        
        if now - last_request < limits["COOLDOWN"] :
            wait_time = limits["COOLDOWN"] - (now - last_request)
            
            if user_id not in dff_cooldown_blocked_groups:
                dff_cooldown_blocked_groups[user_id] = set()
            dff_cooldown_blocked_groups[user_id].add(group_id)
            
            await message.answer(f"⏳ погоди, жди {wait_time:.1f} сек")
            return
        
        dff_media_groups[user_id][group_id] = {
            'docs': [],
            'generation': 0,
            'processing_msg': None,
            'task_started': False
        }
        
        dff_user_cooldowns[user_id] = now
        
        try:
            msg = await message.answer("🔮")
            dff_media_groups[user_id][group_id]['processing_msg'] = msg.message_id
        except Exception as e:
            logger.error(f"failed to send indicator: {str(e)}")
    
    if group_id not in dff_media_groups.get(user_id, {}):
        return
    
    group_data = dff_media_groups[user_id][group_id]
    
    if len(group_data['docs']) >= limits["MAX_FILES_IN_MEDIA_GROUP"]:
        if len(group_data['docs']) == limits["MAX_FILES_IN_MEDIA_GROUP"] and is_new_group:
            try:
                await message.answer("❌ нельзя отправлять больше 10 файлов в одной группе!")
                if group_data['processing_msg']:
                    try:
                        await bot.delete_message(
                            chat_id=message.chat.id,
                            message_id=group_data['processing_msg']
                        )
                    except:
                        pass
            except Exception as e:
                logger.error(f"failed to send error: {str(e)}")
        
        del dff_media_groups[user_id][group_id]
        if not dff_media_groups[user_id]:
            del dff_media_groups[user_id]
        return
    
    group_data['docs'].append(message.document)
    current_generation = group_data['generation']
    
    if not group_data['task_started']:
        group_data['task_started'] = True
        task_key = (user_id, group_id)
        
        task = asyncio.create_task(
            process_dff_media_group(user_id, group_id, current_generation, message.chat.id, bot)
        )
        dff_processing_tasks[task_key] = task
