from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram_dialog import DialogManager, StartMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_conf import database

from states.state_groups import startSG
from database.db_conf import database
from config_data.config import load_config, Config

config: Config = load_config()

db = database('datas.sqlite3')
user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager):
    if not db.check_user(msg.from_user.id):
        db.add_user(msg.from_user.id)
    await dialog_manager.start(state=startSG.start, mode=StartMode.RESET_STACK)


@user_router.message(F.text == 'Отключить интервальный поиск')
async def off_scheduler(msg: Message, scheduler: AsyncIOScheduler):
    jobs = scheduler.get_jobs()
    count = 0
    for job in jobs:
        if job.id.startswith(str(msg.from_user.id)):
            job.remove()
            count += 1
    if count == 0:
        await msg.answer('У вас не запущенно никаких интервальных поисков')
    else:
        await msg.answer('Все запуски были выключены')
