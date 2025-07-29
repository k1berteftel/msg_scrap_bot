from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Column, SwitchTo, Button, Row, Group, Select, Cancel
from aiogram_dialog.widgets.input import MessageInput

from states.state_groups import adminSG
from dialogs.admin_dialog import getters


admin_dialog = Dialog(
    Window(
        Const('Меню админ панели'),
        Column(
            Button(Const('Получить статистику'), id='get_static', on_click=getters.get_static),
            SwitchTo(Const('Сделать рассылку'), id='mail_switcher', state=adminSG.get_mail),
            Cancel(Const('Закрыть админку'), id='close_admin'),
        ),
        state=adminSG.start
    ),
    Window(
        Const('Отправьте сообщение для рассылки'),
        SwitchTo(Const('Назад'), id='back', state=adminSG.start),
        MessageInput(
            func=getters.save_message,
            content_types=ContentType.ANY
        ),
        state=adminSG.get_mail
    ),
    Window(
        Const('Вы подтверждаете рассылку сообщения'),
        Row(
            Button(Const('Да'), id='mallin', on_click=getters.send_message),
            SwitchTo(Const('Нет'), id='back', state=adminSG.start)
        ),
        state=adminSG.confirm_mail
    ),
)