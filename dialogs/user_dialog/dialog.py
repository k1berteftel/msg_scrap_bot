from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Column, SwitchTo, Button, Row, Group, Select
from aiogram_dialog.widgets.input import TextInput

from dialogs.user_dialog.getters import check_account, check_account_del, phone_get, del_account, get_kod, get_password, \
    get_ratio, chats_menu_getter, get_channel, chats_del_getter, channel_selector
from states.state_groups import startSG

user_dialog = Dialog(
    Window(
        Const('Главное меню'),
        Column(
            SwitchTo(Const('Парсинг'), id='parsing', state=startSG.scrap_menu),
            SwitchTo(Const('Управление каналами'), id='channels', state=startSG.channels_menu),
            SwitchTo(Const('Управление аккаунтами для парсинга'), id='account_menu', state=startSG.accounts)
        ),
        state=startSG.start
    ),
    Window(
        Format('Действующий список каналов для парсинга: \n\n {channels}'),
        Column(
            SwitchTo(Const('Добавить канал'), id='change_channels_switch', state=startSG.channel_add),
            SwitchTo(Const('Удалить канал'), id='del_channel_switch', state=startSG.channel_del),
            SwitchTo(Const('Назад'), id='back', state=startSG.start)
        ),
        getter=chats_menu_getter,
        state=startSG.channels_menu
    ),
    Window(
        Const('Требуется ввести идентификатор для канала, а именно:\n'
              '1)Если канал является открытым отправьте ссылку канала\n'
              '2)Если же канала является закрытым отправьте id этого закрытого канала\n\n'
              '<em>Внимание если вы добавляете закрытый канал, надо чтобы аккаунт с которого ведется парсинг данных'
              ' был подписан на данный канал, иначе парсинг закрытого канала будет проигнорирован</em>'),
        TextInput(
            id='channel_get',
            on_success=get_channel
        ),
        SwitchTo(Const('Назад'), id='back_channels', state=startSG.channels_menu),
        state=startSG.channel_add
    ),
    Window(
        Format('{channels}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='chats_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=channel_selector
            ),
            width=2
        ),
        SwitchTo(Const('Назад'), id='back_channels', state=startSG.channels_menu),
        getter=chats_del_getter,
        state=startSG.channel_del
    ),
    Window(
        Const('Введите числовой коэффициент просмотров на репосты, после ввода коэффициента начнется сбор сообщений'),
        SwitchTo(Const('Назад'), id='back', state=startSG.start),
        TextInput(
            id='get_ratio',
            on_success=get_ratio
        ),
        state=startSG.scrap_menu
    ),
    Window(
        Const('Меню привязки аккаунтов'),
        Column(
            Button(Const('Добавить аккаунт'), id='add_account', on_click=check_account),
            Button(Const('Удалить аккаунт'), id='del_account', on_click=check_account_del),
            SwitchTo(Const('Назад'), id='back', state=startSG.start)
        ),
        state=startSG.accounts
    ),
    Window(
        Const('Отправьте номер телефона'),
        SwitchTo(Const('Отмена'), id='back', state=startSG.start),
        TextInput(
            id='get_phone',
            on_success=phone_get,
        ),
        state=startSG.add_account
    ),
    Window(
        Const('Удалить действующий привязанный аккаунт?'),
        Column(
            Button(Const('Да'), id='conf_del_account', on_click=del_account),
            SwitchTo(Const('Назад'), id='back_to_accounts', state=startSG.accounts),
        ),
        state=startSG.del_account
    ),
    Window(
        Const('Введи код который пришел на твой аккаунт в телеграмм в формате: 1-2-3-5-6'),
        TextInput(
            id='get_kod',
            on_success=get_kod,
        ),
        state=startSG.kod_send
    ),
    Window(
        Const('Пароль от аккаунта телеграмм'),
        TextInput(
            id='get_password',
            on_success=get_password,
        ),
        state=startSG.password
    ),
)