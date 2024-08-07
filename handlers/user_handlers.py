from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram_dialog import DialogManager, StartMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_conf import database

from states.state_groups import startSG
from config_data.config import load_config, Config

config: Config = load_config()


user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=startSG.start, mode=StartMode.RESET_STACK)


@user_router.message(F.text == 'Отключить интервальный поиск')
async def off_scheduler(msg: Message, scheduler: AsyncIOScheduler):
    if scheduler.get_job(str(msg.from_user.id)):
        scheduler.remove_job(str(msg.from_user.id))
        await msg.answer('Интервальный поиск был отключен')
        return
    await msg.answer('У вас не запущенно никаких интервальных поисков')