import sqlite3


class database():
    def __init__(self, name):
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()

    def check_user(self, user_id: int):
        with self.connection:
            result = self.cursor.execute('SELECT `user_id` FROM `users` WHERE `user_id` = ?', (user_id, )).fetchmany(1)
        return True if result else False

    def add_user(self, user_id: int):
        with self.connection:
            self.cursor.execute('INSERT INTO `users` (`user_id`) VALUES(?)', (user_id, ))

    def add_account(self, user_id: int, account: str) -> None:
        with self.connection:
            self.cursor.execute('INSERT INTO `accounts` (`user_id`, `account`) VALUES(?, ?)', (user_id, account,))

    def add_chat(self, user_id: int, chat: str):
        with self.connection:
            self.cursor.execute('INSERT INTO `chats` (`chat`, `user_id`) VALUES(?, ?)', (chat, user_id,))

    def add_chat_message_id(self, chat: str, ids: int, user_id: int):
        with self.connection:
            self.cursor.execute('INSERT INTO `ids` (`chat`, `message`, `user_id`) VALUES(?, ?, ?)', (chat, ids, user_id,))

    def add_keyword(self, user_id: int, keyword: str):
        with self.connection:
            self.cursor.execute('INSERT INTO `keywords` (`keyword`, `user_id`) VALUES(?, ?)', (keyword, user_id, ))

    def add_answer(self, user_id: int, answer: str):
        with self.connection:
            self.cursor.execute('INSERT INTO `answers` (`user_id`, `answer`) VALUES(?, ?)', (user_id, answer,))

    def update_answer(self, user_id: int, answer: str):
        with self.connection:
            self.cursor.execute('UPDATE `answers` SET `answer` = ? WHERE `user_id` = ?', (answer, user_id,))

    def update_chat_message_id(self, chat: str, ids: int):
        with self.connection:
            self.cursor.execute('UPDATE `ids` SET `message` = ? WHERE `chat` = ?', (ids, chat, ))

    def get_answer(self, user_id: int):
        with self.connection:
            result = self.cursor.execute('SELECT `answer` FROM `answers` WHERE `user_id` = ?', (user_id,)).fetchmany(1)
        return result[0][0] if result else None

    def get_users(self):
        with self.connection:
            result = self.cursor.execute('SELECT `user_id`, `active` FROM `users`').fetchall()
        return result

    def get_chat_message_id(self, user_id: int, chat: str) -> list[tuple[int]]:
        with self.connection:
            result = self.cursor.execute('SELECT `message` FROM `ids` WHERE `chat` = ? AND `user_id` = ?', (chat, user_id, )).fetchall()
        return result

    def get_keywords(self, user_id: int) -> list[tuple[str]]:
        with self.connection:
            result = self.cursor.execute('SELECT `id`, `keyword` FROM `keywords` WHERE `user_id` == ?', (user_id,)).fetchall()
        return result

    def get_chats(self, user_id: int) -> list[tuple[str]] | bool:
        with self.connection:
            result = self.cursor.execute('SELECT `chat` FROM `chats` WHERE `user_id` = ?', (user_id,)).fetchall()
        return result if result else False

    def get_channels_ids(self, user_id: int) -> list[tuple] | bool:
        with self.connection:
            result = self.cursor.execute('SELECT `id`, `chat` FROM `chats` WHERE `user_id` = ?', (user_id,)).fetchall()
        return result if result else False

    def get_chats_show(self, user_id: int) -> list[tuple[int, str]] | bool:
        with self.connection:
            result = self.cursor.execute('SELECT `id`, `chat` FROM `chats` WHERE `user_id` = ?', (user_id,)).fetchall()
        return result if result else False

    def get_account(self, user_id: int) -> str | None:
        with self.connection:
            result = self.cursor.execute('SELECT `account` FROM `accounts` WHERE `user_id` = ?', (user_id, )).fetchmany(1)
        print(result)
        return result[0][0] if result else None

    def set_active(self, user_id: int, active: int):
        with self.connection:
            self.cursor.execute('UPDATE `users` SET `active` = ? WHERE `user_id` = ?', (active, user_id, ))

    def del_answer(self, user_id: int):
        with self.connection:
            self.cursor.execute('DELETE FROM `answers` WHERE `user_id` = ?', (user_id, ))

    def del_keyword(self, id: int):
        with self.connection:
            self.cursor.execute('DELETE FROM `keywords` WHERE `id` = ? ', (id, ))

    def del_account(self, user_id: int):
        with self.connection:
            self.cursor.execute('DELETE FROM `accounts` WHERE `user_id` = ?', (user_id, ))

    def del_chat(self, chat: str, user_id: int):
        with self.connection:
            self.cursor.execute('DELETE FROM `chats` WHERE `chat` = ? AND `user_id` = ?', (chat, user_id,))

    def del_database(self):
        with self.connection:
            self.cursor.execute('DELETE FROM `accounts`')
            self.cursor.execute('DELETE FROM `chats`')
            self.cursor.execute('DELETE FROM `keywords`')
            self.cursor.execute('DELETE FROM `ids`')
