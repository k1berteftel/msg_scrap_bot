import datetime
import os
from aiogram import Bot
from aiogram.types import Message, User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from states.state_groups import adminSG
from database.db_conf import database


db = database('datas.sqlite3')


async def get_static(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    users = db.get_users()
    active = 0
    for user in users:
        if user[1]:
            active += 1
    text = f'Всего юзеров: {len(users)}\nИз них активных: {active}'
    await clb.message.answer(text)


async def save_message(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['message'] = msg
    await dialog_manager.switch_to(adminSG.confirm_mail)


async def send_message(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    message: Message = dialog_manager.dialog_data.get('message')
    users = db.get_users()
    for user in users:
        try:
            await message.send_copy(chat_id=user[0])
            if user[1] == 0:
                db.set_active(user[0], 1)
        except Exception as err:
            db.set_active(user[0], 0)

    await clb.message.answer('Рассылка прошла успешно')
    await dialog_manager.switch_to(adminSG.start)
