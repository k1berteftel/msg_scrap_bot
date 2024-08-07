import sqlite3


class database():
    def __init__(self, name):
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()

    def add_account(self, user_id: int, account: str) -> None:
        with self.connection:
            self.cursor.execute('INSERT INTO `accounts` (`user_id`, `account`) VALUES(?, ?)', (user_id, account,))

    def add_chat(self, chat: str):
        with self.connection:
            self.cursor.execute('INSERT INTO `chats` (`chat`) VALUES(?)', (chat,))

    def add_chat_message_id(self, chat: str, ids: int):
        with self.connection:
            self.cursor.execute('INSERT INTO `ids` (`chat`, `message`) VALUES(?, ?)', (chat, ids, ))

    def update_chat_message_id(self, chat: str, ids: int):
        with self.connection:
            self.cursor.execute('UPDATE `ids` SET `message` = ? WHERE `chat` = ?', (ids, chat, ))

    def get_chat_message_id(self, chat: str) -> int | bool:
        with self.connection:
            result = self.cursor.execute('SELECT `message` FROM `ids` WHERE `chat` = ?', (chat, )).fetchmany(1)
        return int(result[0][0]) if result else False

    def get_chats(self) -> list[tuple[str]] | bool:
        with self.connection:
            result = self.cursor.execute('SELECT `chat` FROM `chats`').fetchall()
        return result if result else False

    def get_channels_ids(self) -> list[tuple] | bool:
        with self.connection:
            result = self.cursor.execute('SELECT `id`, `chat` FROM `chats`').fetchall()
        return result if result else False

    def get_chats_show(self) -> list[tuple[int, str]] | bool:
        with self.connection:
            result = self.cursor.execute('SELECT `id`, `chat` FROM `chats`').fetchall()
        return result if result else False

    def get_account(self, user_id: int) -> str | None:
        with self.connection:
            result = self.cursor.execute('SELECT `account` FROM `accounts` WHERE `user_id` = ?', (user_id, )).fetchmany(1)
        print(result)
        return result[0][0] if result else None

    def del_account(self, user_id: int):
        with self.connection:
            self.cursor.execute('DELETE FROM `accounts` WHERE `user_id` = ?', (user_id, ))

    def del_chat(self, chat: str):
        with self.connection:
            self.cursor.execute('DELETE FROM `chats` WHERE `chat` = ?', (chat, ))

    def del_database(self):
        with self.connection:
            self.cursor.execute('DELETE FROM `accounts`')