import datetime
import os
from aiogram import Bot
from aiogram.types import Message, User, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput
from pyrogram import Client
from pyrogram.types import SentCode
from pyrogram.errors import PasswordHashInvalid
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.db_conf import database
from config_data.config import load_config, Config
from states.state_groups import startSG
from utils.pars_functions import get_messages
from utils.account_functions import get_channels, get_chat


config: Config = load_config()
api_id = 9238838
api_hash = 'b65e9edfabe1c645a0d101543f065e89'
db = database('datas.sqlite3')


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    admin = False
    if event_from_user.id in config.bot.admins:
        admin = True
    return {'admin': admin}


async def every_day_get(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    job_id = scheduler.get_job(job_id=f'{msg.from_user.id}_cron')
    time = text.split(':')
    if len(time) != 2:
        await msg.answer('Вы ввели данные не в том формате пожалуйста попробуйте снова')
        return
    try:
        hour = int(time[0])
        minute = int(time[1])
    except Exception:
        await msg.answer('Вы ввели данные не в том формате пожалуйста попробуйте снова')
        return
    if hour not in range(0, 24) or minute not in range(0, 61):
        await msg.answer('Вы ввели данные не в том формате пожалуйста попробуйте снова')
        return
    bot: Bot = dialog_manager.middleware_data.get('bot')
    account = db.get_account(msg.from_user.id)
    keywords = [i[1] for i in db.get_keywords(msg.from_user.id)]
    if not keywords:
        await msg.answer('У вас не добавлено ключевых слов для фильтрации')
        return
    if not account:
        await msg.answer('У вас не привязано аккаунтов для парсинга')
        return
    chats = db.get_chats(msg.from_user.id)
    if not chats:
        await msg.answer('Нету чатов для сбора информации\nПожалуйста добавьте чаты перед тем как начинать сбор')
        return
    print(job_id)
    if job_id:
        job_id.remove()
        await msg.answer('Прошлый ежедневный поиск был успешно выключен')
    channels = []
    for chat in chats:
        try:
            chat = int(chat[0])
            channels.append(chat)
        except Exception as err:
            channels.append(chat[0])
            print(err)

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отключить интервальный поиск')]], resize_keyboard=True)
    await msg.answer('Процесс парсинга был запущен', reply_markup=keyboard)
    scheduler.add_job(
        get_messages,
        'cron',
        args=[account, channels, bot, keywords, msg.from_user.id],
        hour=hour,
        minute=minute,
        id=f'{msg.from_user.id}_cron'
    )
    await dialog_manager.switch_to(startSG.scrap_menu)


async def interval_get(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    job_id = scheduler.get_job(job_id=f'{msg.from_user.id}_interval')
    interval = text.split(':')
    if len(interval) != 2:
        await msg.answer('Вы ввели данные не в том формате пожалуйста попробуйте снова')
        return
    try:
        minutes = int(interval[0]) * 60 + int(interval[1])
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате пожалуйста попробуйте снова')
        return
    bot: Bot = dialog_manager.middleware_data.get('bot')
    account = db.get_account(msg.from_user.id)
    keywords = [i[1] for i in db.get_keywords(msg.from_user.id)]
    if not keywords:
        await msg.answer('У вас не добавлено ключевых слов для фильтрации')
        return
    if not account:
        await msg.answer('У вас не привязано аккаунтов для парсинга')
        return
    chats = db.get_chats(msg.from_user.id)
    if not chats:
        await msg.answer('Нету чатов для сбора информации\nПожалуйста добавьте чаты перед тем как начинать сбор')
        return
    print(job_id)
    if job_id:
        job_id.remove()
        await msg.answer('Прошлый ежедневный поиск был успешно выключен')
    channels = []
    for chat in chats:
        try:
            chat = int(chat[0])
            channels.append(chat)
        except Exception as err:
            channels.append(chat[0])
            print(err)
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отключить интервальный поиск')]], resize_keyboard=True)

    scheduler.add_job(
        get_messages,
        'interval',
        args=[account, channels, bot, keywords, msg.from_user.id],
        minutes=minutes,
        id=f'{msg.from_user.id}_interval'
    )
    await msg.answer('Процесс парсинга был запущен', reply_markup=keyboard)
    await dialog_manager.switch_to(startSG.scrap_menu)


async def one_time_pars(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data.get('bot')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    account = db.get_account(clb.from_user.id)
    # проверка на ключевые слова
    keywords = [i[1] for i in db.get_keywords(clb.from_user.id)]
    print(keywords)
    if not keywords:
        await clb.answer('У вас не добавлено ключевых слов для фильтрации')
        return
    if not account:
        await clb.message.answer('У вас не привязано аккаунтов для парсинга')
        return
    chats = db.get_chats(clb.from_user.id)
    if not chats:
        await clb.message.answer('Нету чатов для сбора информации\nПожалуйста добавьте чаты перед тем как начинать сбор')
        return
    channels = []
    for chat in chats:
        try:
            chat = int(chat[0])
            channels.append(chat)
        except Exception as err:
            channels.append(chat[0])
            print(err)
    await clb.message.answer('Начался процесс парсинга')
    await get_messages(account, channels, bot, keywords, clb.from_user.id)


async def answers_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    answer = db.get_answer(event_from_user.id)
    text = 'Отсутствует'
    if answer:
        text = answer
    return {
        'text': text,
        'answer': bool(answer),
        'not_answer': not bool(answer)
    }


async def delete_answering(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    db.del_answer(clb.from_user.id)
    await clb.answer('Ваш автоответ был успешно удален')


async def get_answer_text(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    db.add_answer(msg.from_user.id, text)
    await msg.answer('Ваш автоответ был успешно добавлен')
    await msg.delete()
    await dialog_manager.switch_to(startSG.answering_menu)


async def update_answer_text(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    db.update_answer(msg.from_user.id, text)
    await msg.answer('Ваш автоответ был успешно обновлен')
    await msg.delete()
    await dialog_manager.switch_to(startSG.answering_menu)


async def keyword_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    dirty_keywords = db.get_keywords(event_from_user.id)
    keywords = [i[1] for i in dirty_keywords]
    text = ''
    count = 1
    for keyword in keywords:
        text += f'{count}: {keyword}\n'
        count += 1
    return {'text': text}


async def keyword_get(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    keywords = text.strip().split('\n')
    for keyword in keywords:
        db.add_keyword(msg.from_user.id, keyword)
    await msg.answer('Ключевые слова были успешно добавлены')
    await dialog_manager.switch_to(startSG.keywords_menu)


async def keyword_del(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    id = int(item_id)
    db.del_keyword(id)
    await clb.answer('Ключевое слово было успешно удаленно')
    await dialog_manager.switch_to(startSG.keywords_menu)


async def keyword_del_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    keywords = db.get_keywords(event_from_user.id)
    buttons = []
    text = ''
    count = 1
    for keyword in keywords:
        buttons.append((str(count), str(keyword[0])))
        text += f'{count}: {keyword[1]}\n'
        count += 1
    return {
        'items': buttons,
        'text': text
    }


async def channel_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    chats: list[tuple[str]] = dialog_manager.dialog_data.get('chats')
    for chat in chats:
        if chat[0] == int(item_id):
            db.del_chat(chat[1], clb.from_user.id)
    await clb.answer('Канал был успешно удален')


async def chats_del_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    chats = db.get_chats_show(event_from_user.id)
    text = 'Введите канал который вы хотели бы удалить\n\n'
    chat_buttons = []
    if chats:
        for chat in chats:
            chat_buttons.append((chat[1], chat[0]))
            text += f'{chat[0]}: {chat[1]}\n'
    else:
        text = 'Каналы отсутствуют'
    dialog_manager.dialog_data['chats'] = chats
    return {'channels': text,
            'items': chat_buttons}


async def get_channel(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        chat = int(text)
    except Exception as err:
        try:
            chat = text.split('/')[-1]
        except Exception as err:
            await message.answer('Введенный формат данных неверен')
            return
    db.add_chat(message.from_user.id, str(chat))
    await message.answer('Канал был успешно добавлен')
    await dialog_manager.switch_to(startSG.channels_menu)


async def my_channels_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    page = dialog_manager.dialog_data.get('chat_page')
    account = db.get_account(event_from_user.id)
    bot: Bot = dialog_manager.middleware_data.get('bot')
    if not account:
        await bot.send_message(
            chat_id=event_from_user.id,
            text='У вас не привязано аккаунтов для парсинга'
        )
        await dialog_manager.switch_to(startSG.accounts)
        return
    bot: Bot = dialog_manager.middleware_data.get('bot')
    if not page:
        page = 0
        dialog_manager.dialog_data['chat_page'] = page
    dialogs = dialog_manager.dialog_data.get('chats')
    if not dialogs:
        dialogs = await get_channels(account, bot, event_from_user.id)
        dialogs = [dialogs[i:i + 20] for i in range(0, len(dialogs), 20)]
        dialog_manager.dialog_data['chats'] = dialogs
    not_first = True
    not_last = True
    if page == 0:
        not_first = False
    if page == len(dialogs) - 1:
        not_last = False
    return {
        'items': dialogs[page],
        'not_first': not_first,
        'not_last': not_last,
        'open_page': str(page + 1),
        'last_page': str(len(dialogs))
    }


async def my_channels_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    page = dialog_manager.dialog_data.get('chat_page')
    if clb.data.startswith('back'):
        dialog_manager.dialog_data['chat_page'] = page - 1
    else:
        dialog_manager.dialog_data['chat_page'] = page + 1
    await dialog_manager.switch_to(startSG.my_channels)


async def my_chat_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    db.add_chat(clb.from_user.id, item_id)
    await clb.answer('Канал был успешно добавлен')
    await dialog_manager.switch_to(startSG.channels_menu)


async def chats_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    chats = db.get_chats(event_from_user.id)
    count = 1
    text = ''
    if chats:
        for chat in chats:
            text += f'{count}: {chat[0]}\n'
            count += 1
    else:
        text = 'Каналы отсутствуют'
    return {'channels': text}


async def get_ratio(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    bot: Bot = dialog_manager.middleware_data.get('bot')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    try:
        ratio = float(text)
    except Exception:
        await message.answer('Вы ввели не число, пожалуйста попробуйте еще раз')
        return
    account = db.get_account(message.from_user.id)
    if not account:
        await message.answer('У вас не привязано аккаунтов для парсинга')
        return
    chats = db.get_chats(message.from_user.id)
    if not chats:
        await message.answer('Нету чатов для сбора информации\nПожалуйста добавьте чаты перед тем как начинать сбор')
        return
    channels = []
    for chat in chats:
        try:
            chat = int(chat[0])
            channels.append(chat)
        except Exception as err:
            channels.append(chat[0])
            print(err)
    await message.answer('Начался поиск, пожалуйста ожидайте')
    if not scheduler.get_job(job_id=str(message.from_user.id)):
        print('scheduler start work')
        scheduler.add_job(get_messages, 'interval',
                          args=[account, ratio, channels, bot, scheduler, message], minutes=10, id=str(message.from_user.id))
    #messages = await get_messages(account, ratio, channels, bot, scheduler, message.from_user.id)

    reply_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отключить интервальный поиск')]], resize_keyboard=True)
    await message.answer('Интервальный процесс поиска был запущен, каждые 10 минут бот будет просматривать наличие подходящих постов', reply_markup=reply_keyboard)
    await dialog_manager.switch_to(startSG.start)
    return
    #await message.answer(f'⭐️{msg[0]}|❤️{msg[1]}|✈️{msg[2]}|👍{msg[3]}|👀{msg[4]}|🔗<a href="{msg[5]}">ссылка</a>', disable_notification=True, disable_web_page_preview=True)
    #messages.insert(0, ['репосты / просмотры', 'реакции / просмотры', 'репосты', 'реакции', 'просмотры', 'ссылка на пост'])


async def del_account(clb: CallbackQuery, button: Button, dialog_manager: DialogManager):
    account = db.get_account(user_id=clb.from_user.id)
    db.del_account(clb.from_user.id)
    try:
        os.remove(f'{account}.session')
    except Exception as err:
        print(err)
    await dialog_manager.switch_to(state=startSG.accounts)


async def check_account_del(clb: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not db.get_account(clb.from_user.id):
        await clb.answer('У вас отсутствует аккаунт для удаления')
        return
    await dialog_manager.switch_to(state=startSG.del_account)


async def check_account(clb: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if db.get_account(clb.from_user.id):
        await clb.answer('Вы уже имеете привязанный аккаунт')
        return
    await dialog_manager.switch_to(state=startSG.add_account)


async def phone_get(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    print('Начало соединения')
    client = Client(f'{message.from_user.id}', api_id, api_hash)
    await client.connect()
    print(text, type(text))
    try:
        print('Отправка кода')
        sent_code_info: SentCode = await client.send_code(text.strip())
    except Exception as err:
        print(err)
        await message.answer('Веденный номер телефона неверен, попробуйте снова')
        return
    dialog_manager.dialog_data['client'] = client
    dialog_manager.dialog_data['phone_info'] = sent_code_info
    dialog_manager.dialog_data['phone_number'] = text
    await dialog_manager.switch_to(state=startSG.kod_send)


async def get_kod(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    client: Client = dialog_manager.dialog_data.get('client')
    phone_info: SentCode = dialog_manager.dialog_data.get('phone_info')
    phone = dialog_manager.dialog_data.get('phone_number')
    code = ''
    if len(text.split('-')) != 5:
        await message.answer(text='Вы отправили код в неправильном формате, попробуйте вести код снова')
        return
    for number in text.split('-'):
        code += number
    print(code)
    try:
        await client.sign_in(phone, phone_info.phone_code_hash, code)
        await client.disconnect()
        db.add_account(message.from_user.id, account=str(message.from_user.id))
        dialog_manager.dialog_data.clear()
        await dialog_manager.switch_to(state=startSG.accounts)
    except Exception as err:
        print(err)
        await dialog_manager.switch_to(state=startSG.password)


async def get_password(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    client: Client = dialog_manager.dialog_data.get('client')
    phone_info = dialog_manager.dialog_data.get('phone_info')
    phone = dialog_manager.dialog_data.get('phone_number')

    try:
        await client.check_password(text)
        await client.disconnect()
        db.add_account(message.from_user.id, account=str(message.from_user.id))
        await message.answer(text='Ваш аккаунт был успешно добавлен')
        dialog_manager.dialog_data.clear()
        await dialog_manager.switch_to(state=startSG.accounts)
    except PasswordHashInvalid as err:
        print(err)
        await message.answer(text='Введенные данные были неверны, пожалуйста попробуйте авторизоваться снова')
        await dialog_manager.switch_to(state=startSG.add_account)
