from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Column, SwitchTo, Button, Row, Group, Select, Start
from aiogram_dialog.widgets.input import TextInput

from dialogs.user_dialog import getters
from states.state_groups import startSG, adminSG

user_dialog = Dialog(
    Window(
        Const('<b>📋Инструкция по использованию бота:</b>\n\n1️⃣Перейди в меню управления '
              'аккаунтом для парсинга нажав на <em>`💬Управление аккаунтом для парсинга`</em> и добавь в бота '
              'аккаунт через который в последствии будет происходить парсинг\n\n2️⃣Перейди '
              'в <em>`💼Управление каналами`</em> и добавь один или несколько каналов в которых нужно будет вести поиск'
              '\n\n3️⃣Перейди в <em>`🔗Управление ключевыми словами`</em> и добавь несколько ключевых '
              'слов по которым нужно будет сортировать сообщения\n\n'
              '4️⃣При необходимости ты можешь добавить автоответ на сообщения подобранные парсером, '
              'чтобы после удачной сортировки сообщения бот от лица твоего аккаунта писал заранее заготовленное '
              'сообщение юзеру чье сообщение было удачно отсортировано парсером\n\n<b>Удачного пользования</b>'),
        Column(
            SwitchTo(Const('⚙️Настройка парсинга'), id='parsing', state=startSG.scrap_menu),
            SwitchTo(Const('💬Управление автоответом'), id='answering_switcher', state=startSG.answering_menu),
            SwitchTo(Const('💼Управление каналами'), id='channels', state=startSG.channels_menu),
            SwitchTo(Const('🔗Управление ключевыми словами'), id='keywords_menu_switcher', state=startSG.keywords_menu),
            SwitchTo(Const('👤Управление аккаунтом для парсинга'), id='account_menu', state=startSG.accounts),
            Start(Const('Админ панель'), id='admin_menu', state=adminSG.start, when='admin')
        ),
        getter=getters.start_getter,
        state=startSG.start
    ),
    Window(
        Const('<b>Меню управления парсингом</b>'),
        Column(
            Button(Const('⚡️Разовый парсинг'), id='one_time_pars', on_click=getters.one_time_pars),
            SwitchTo(Const('🕜Интервальный парсинг'), id='interval_pars', state=startSG.interval_get),
            SwitchTo(Const('🌥Ежедневный парсинг'), id='every_day_pars', state=startSG.every_day_get),
            SwitchTo(Const('🔙Назад'), id='back', state=startSG.start)
        ),
        state=startSG.scrap_menu
    ),
    Window(
        Const('Отправьте время в которое каждый день вы будете получать результаты парсинга\nОтправьте временной промежуток'
              ' в формате 02:30 (часы:минуты)'),
        TextInput(
            id='get_time',
            on_success=getters.every_day_get
        ),
        SwitchTo(Const('🔙Назад'), id='back_scrap_menu', state=startSG.scrap_menu),
        state=startSG.every_day_get
    ),
    Window(
        Const('Введите интервал через который будет происходить парсинг\nОтправьте временной промежуток'
              ' в формате 02:30 (часы:минуты)'),
        TextInput(
            id='get_interval',
            on_success=getters.interval_get
        ),
        SwitchTo(Const('🔙Назад'), id='back_scrap_menu', state=startSG.scrap_menu),
        state=startSG.interval_get
    ),
    Window(
        Const('<b>Меню управления автоответами</b>'),
        Format('<b>Действующий автоответ</b>:\n {text}'),
        Column(
            SwitchTo(Const('➕Добавить автоответ'), id='add_answer_switcher', state=startSG.answer_add_text, when='not_answer'),
            SwitchTo(Const('✏️Редактировать автоответ'), id='redact_answer_switcher', state=startSG.answer_redact, when='answer'),
            Button(Const('🗑Удалить автоответ'), id='delete_answer', on_click=getters.delete_answering, when='answer'),
        ),
        SwitchTo(Const('🔙Назад'), id='back', state=startSG.start),
        getter=getters.answers_menu_getter,
        state=startSG.answering_menu
    ),
    Window(
        Const('Введите автоответ, который будет приходить владельцам сообщений,'
              ' которые подходят под ваши ключевые слова\n<em>Автоответ будет происходить с '
              'привязанного вами аккаунта для парсинга</em>'),
        TextInput(
            id='get_answer_text',
            on_success=getters.get_answer_text
        ),
        SwitchTo(Const('🔙Назад'), id='back_answering_menu', state=startSG.answering_menu),
        state=startSG.answer_add_text
    ),
    Window(
        Const('Введите новый автоответ'),
        TextInput(
            id='update_answer_text',
            on_success=getters.update_answer_text
        ),
        SwitchTo(Const('🔙Назад'), id='back_answering_menu', state=startSG.answering_menu),
        state=startSG.answer_redact
    ),
    Window(
        Format('Действующий список ключевых слов:\n{text}'),
        Column(
            SwitchTo(Const('➕Добавить ключевое слово'), id='add_keyword_switcher', state=startSG.keyword_add),
            SwitchTo(Const('🗑Удалить ключевое слово'), id='del_keyword_switcher', state=startSG.keyword_del),
            SwitchTo(Const('🔙Назад'), id='back', state=startSG.start)
        ),
        getter=getters.keyword_menu_getter,
        state=startSG.keywords_menu
    ),
    Window(
        Const('Введите ключевое слово или словосочетание\n<em>Для добавления нескольких'
              ' отправьте слова или словосочетания через абзац например</em>:\n'
              'Аппарат\nСтроительные кирпичи'),
        TextInput(
            id='keyword_get',
            on_success=getters.keyword_get
        ),
        SwitchTo(Const('🔙Назад'), id='back_keyword_menu', state=startSG.keywords_menu),
        state=startSG.keyword_add
    ),
    Window(
        Format('Чтобы удалить ключевое слово выберите пункт под которым ключевое слово находится:\n{text}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='keyword_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.keyword_del
            ),
            width=1
        ),
        SwitchTo(Const('🔙Назад'), id='back_keyword_menu', state=startSG.keywords_menu),
        getter=getters.keyword_del_getter,
        state=startSG.keyword_del
    ),
    Window(
        Format('Действующий список каналов для парсинга:\n\n{channels}'),
        Column(
            SwitchTo(Const('➕Добавить канал'), id='change_channels_switch', state=startSG.channel_add),
            SwitchTo(Const('🗑Удалить канал'), id='del_channel_switch', state=startSG.channel_del),
            SwitchTo(Const('🔙Назад'), id='back', state=startSG.start)
        ),
        getter=getters.chats_menu_getter,
        state=startSG.channels_menu
    ),
    Window(
        Const('Требуется ввести идентификатор для канала, а именно:\n\n'
              '1️⃣Если канал является открытым отправьте ссылку канала\n'
              '2️⃣Если же канала является закрытым отправьте id этого закрытого канала\n\n'
              '<em>!!Внимание если вы добавляете закрытый канал, надо чтобы аккаунт с которого ведется парсинг данных'
              ' был подписан на данный канал, иначе парсинг закрытого канала будет проигнорирован</em>'),
        TextInput(
            id='channel_get',
            on_success=getters.get_channel
        ),
        SwitchTo(Const('Мои чаты и каналы'), id='my_channels_switcher', state=startSG.my_channels),
        SwitchTo(Const('🔙Назад'), id='back_channels', state=startSG.channels_menu),
        state=startSG.channel_add
    ),
    Window(
        Const('Выберите канал | чат'),
        Group(
            Select(
                Format('{item[0]}'),
                id='my_chats_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.my_chat_selector
            ),
            width=1
        ),
        Row(
            Button(Const('<'), id='back_my_chat_pager', on_click=getters.my_channels_pager, when='not_first'),
            Button(Format('{open_page}/{last_page}'), id='pager'),
            Button(Const('>'), id='next_my_chat_pager', on_click=getters.my_channels_pager, when='not_last'),
        ),
        SwitchTo(Const('🔙Назад'), id='back_channel_add', state=startSG.channel_add),
        getter=getters.my_channels_getter,
        state=startSG.my_channels
    ),
    Window(
        Format('{channels}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='chats_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.channel_selector
            ),
            width=2
        ),
        SwitchTo(Const('🔙Назад'), id='back_channels', state=startSG.channels_menu),
        getter=getters.chats_del_getter,
        state=startSG.channel_del
    ),
    Window(
        Const('<b>Меню привязки аккаунтов</b>'),
        Column(
            Button(Const('➕Добавить аккаунт'), id='add_account', on_click=getters.check_account),
            Button(Const('🗑Удалить аккаунт'), id='del_account', on_click=getters.check_account_del),
            SwitchTo(Const('🔙Назад'), id='back', state=startSG.start)
        ),
        state=startSG.accounts
    ),
    Window(
        Const('Отправьте номер телефона'),
        SwitchTo(Const('Отмена'), id='back', state=startSG.start),
        TextInput(
            id='get_phone',
            on_success=getters.phone_get,
        ),
        state=startSG.add_account
    ),
    Window(
        Const('Удалить действующий привязанный аккаунт?'),
        Column(
            Button(Const('✅Да'), id='conf_del_account', on_click=getters.del_account),
            SwitchTo(Const('🔙Назад'), id='back_to_accounts', state=startSG.accounts),
        ),
        state=startSG.del_account
    ),
    Window(
        Const('Введи код который пришел на твой аккаунт в телеграмм в формате: 1-2-3-5-6'),
        TextInput(
            id='get_kod',
            on_success=getters.get_kod,
        ),
        state=startSG.kod_send
    ),
    Window(
        Const('Пароль от аккаунта телеграмм'),
        TextInput(
            id='get_password',
            on_success=getters.get_password,
        ),
        state=startSG.password
    ),
)