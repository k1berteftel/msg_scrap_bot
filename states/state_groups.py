from aiogram.fsm.state import State, StatesGroup


class startSG(StatesGroup):
    start = State()
    answering_menu = State()
    answer_add_text = State()
    answer_redact = State()
    answer_del = State()
    keywords_menu = State()
    keyword_add = State()
    keyword_del = State()
    channels_menu = State()
    my_channels = State()
    channel_del = State()
    channel_add = State()
    accounts = State()
    add_account = State()
    del_account = State()
    kod_send = State()
    password = State()
    scrap_menu = State()
    interval_get = State()
    every_day_get = State()


class adminSG(StatesGroup):
    start = State()
    get_mail = State()
    confirm_mail = State()