import openpyxl
from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.types import MessageReactions

from database.db_conf import database

db = database('datas')
api_id = 1342
api_hash = ''
#chats = [
#    'mostoday', 'radiogovoritmsk', 'mosnow8', 'mosjournal', 'moscowmap', 'mosguru',
#    'moscowachplus', -1001747110091, -1001976952674
#]


async def get_messages(account: str, ratio: int | float, chats: list[str | int], bot: Bot, scheduler: AsyncIOScheduler,
                       msgs: Message) -> list[list] | bool:
    messages = []
    try:
        app = Client(account)
    except Exception as err:
        print(err)
        await msgs.answer(
            text='Срок привязанного аккаунта подошел к концу, пожалуйста удалите из бота существующий и привяжите его снова'
        )
        return False
    async with app:
        for chat in chats:
            counter = 1
            message_id = db.get_chat_message_id(str(chat))
            try:
                async for message in app.get_chat_history(chat_id=chat, limit=25):
                    try:
                        if counter == 1:
                            if message_id:
                                db.update_chat_message_id(str(chat), message.id)
                            else:
                                db.add_chat_message_id(str(chat), message.id)
                        print(message_id, message.id)
                        if message_id and message_id - 4 >= message.id:
                            print('success stop')
                            break
                        counter += 1
                        viewers = message.views
                        reposts = message.forwards
                        if reposts / viewers > ratio:
                            reactions: MessageReactions = message.reactions
                            count = 0
                            if reactions:
                                for reaction in reactions.reactions:
                                    count += reaction.count
                            messages.append([
                                round(reposts / viewers, 3),
                                round(count / viewers, 3) if count else 'отсутствует',
                                reposts,
                                count if count else 'отсутствует',
                                viewers,
                                message.link
                            ])
                    except Exception as err:
                        print(err)
                        continue
            except Exception as err:
                print(err)
                continue
    for msg in messages:
        await msgs.answer(f'⭐️{msg[0]}|❤️{msg[1]}|✈️{msg[2]}|👍{msg[3]}|👀{msg[4]}|🔗<a href="{msg[5]}">ссылка</a>', disable_notification=True, disable_web_page_preview=True)


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
