import openpyxl
import pyrogram
from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.errors import BadMsgNotification
from pyrogram.types import MessageReactions

from database.db_conf import database

db = database('datas.sqlite3')
api_id = 9238838
api_hash = 'b65e9edfabe1c645a0d101543f065e89'


async def get_messages(account: str, chats: list[str | int], bot: Bot, keywords: list[str], user_id: int, scheduler: AsyncIOScheduler=None) -> list[list] | bool:
    messages = []
    try:
        app = Client(account)
    except Exception as err:
        print(err)
        await bot.send_message(
            chat_id=user_id,
            text='Срок привязанного аккаунта подошел к концу, пожалуйста удалите из бота существующий и привяжите его снова'
        )
        return False
    async with app:
        for chat in chats:
            message_ids = [i[0] for i in db.get_chat_message_id(user_id, chat)]
            async for message in app.get_chat_history(chat_id=chat, limit=50):
                if message.text:
                    for keyword in keywords:
                        if keyword.lower() in message.text.lower():
                            if message.id not in message_ids:
                                db.add_chat_message_id(chat, message.id, user_id)
                            else:
                                continue
                            await write_customer(app, message.from_user.id, user_id)
                            messages.append([
                                message.text,
                                message.from_user.username if message.from_user.username else message.link
                            ])
    for message in messages:
        link = message[1] if message[1].startswith('http') else '@' + message[1]
        text = f'{message[0]} \n\nИсточник:{link}'
        await bot.send_message(
            chat_id=user_id,
            text=text
        )
    #if not messages:
        #await bot.send_message(chat_id=user_id, text='К сожалению совпадений не было найдено')


def get_table(tables: list[list], ) -> str:
    """
        Возвращает путь к файлу таблицы
    """
    wb = openpyxl.Workbook()
    sheet = wb.active

    for row in range(0, len(tables)):
        for column in range(0, len(tables[row])):
            c1 = sheet.cell(row=row + 1, column=column + 1)
            c1.value = tables[row][column]
    wb.save(f'static.xlsx')
    return f'static.xlsx'


async def write_customer(app: pyrogram.Client, chat_id: int, user_id: int):
    answer = db.get_answer(user_id)
    if not answer:
        return
    await app.send_message(
        chat_id=chat_id,
        text=answer
    )

