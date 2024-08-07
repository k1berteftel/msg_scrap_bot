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
from states.state_groups import startSG
from utils.pars_functions import get_messages, get_table


api_id = 9238838
api_hash = 'b65e9edfabe1c645a0d101543f065e89'
db = database('datas')


async def channel_selector(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    chats: list[tuple[str]] = dialog_manager.dialog_data.get('chats')
    for chat in chats:
        if chat[0] == int(item_id):
            db.del_chat(chat[1])
    await clb.answer('Канал был успешно удален')


async def chats_del_getter(dialog_manager: DialogManager, **kwargs):
    chats = db.get_chats_show()
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
    db.add_chat(str(chat))
    await message.answer('Канал был успешно добавлен')
    await dialog_manager.switch_to(startSG.channels_menu)


async def chats_menu_getter(dialog_manager: DialogManager, **kwargs):
    chats = db.get_chats()
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
    chats = db.get_chats()
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
        os.remove(account)
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
    client = Client(f'{message.from_user.id}', api_id, api_hash)
    await client.connect()
    print(text, type(text))
    try:
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
