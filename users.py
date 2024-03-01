from core.db_pool import db
# from core.db import db
# from core.db_ssh import db

from core import core_log as log
import os
import inspect


class Users:
    def __init__(self):
        self.users_id = []
        # self.admins_id = [5107502329, 414366402]
        self.admins_id = [5107502329]

    async def set(self) -> None:
        """
        Заполнение списка users_id из БД
        :return: None
        """
        try:
            # очистка
            self.users_id.clear()
            query = 'select tg_id from users where active = TRUE'
            # await db.connect()
            rows = await db.fetch(query=query)
            # await db.disconnect()
            for tg_id in rows:
                self.users_id.append(tg_id[0])
        except Exception as err:
            await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                          facility=os.path.basename(__file__))

    async def add_admin(self, admin_id: int) -> None:
        """
        Добавление нового admin_id бота
        :return: None
        """
        self.admins_id.append(admin_id)

    async def add(self, user: dict) -> bool:
        """
        Регистрация нового пользователя бота. Добавляет пользователя в БД, добавляет id пользователя в список
        :param user: пользователь (словарь{id, full_name})
        :return: bool
        """
        try:
            # добавляем id пользователя
            self.users_id.append(user.get('id'))
            # ищем пользователя в таблице users по telegram_id
            query = f"SELECT active from users where tg_id = {user.get('id')}"
            # await db.connect()
            rows = await db.fetch(query=query)
            # await db.disconnect()
            # если пользователь есть, то возвращаем ему активность
            if rows:
                query = f"UPDATE users SET active = True WHERE tg_id = {user.get('id')}"
            # иначе записываем нового пользователя в таблицу users БД
            else:
                query = f"INSERT INTO users (name, tg_id, active) VALUES ('{user.get('full_name')}', {user.get('id')}, True)"
            # print(query)
            # await db.connect()
            await db.execute(query=query)
            # await db.disconnect()
            return True

        except Exception as err:
            await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                          facility=os.path.basename(__file__))

    async def get(self, admins: bool = False) -> list:
        """
        Получить telegram_id зарегистрированных пользователей
        :param admins: получить id админов бота
        :return: list
        """
        if admins:
            return self.admins_id
        return self.users_id

    async def deactivate(self, user_id: int) -> str:
        """
        Отписаться
        :param user_id: id пользователя
        :return: str
        """
        try:
            if user_id in self.users_id:
                self.users_id.remove(user_id)
                # делаем пользователя неактивным в таблице users БД
                query = f"UPDATE users SET active = False WHERE tg_id = {user_id}"
                # await db.connect()
                await db.execute(query=query)
                # await db.disconnect()
                return 'Вы успешно отписаны от бота'
            else:
                return 'В списке подписчиков вас нет'

        except Exception as err:
            await log.log(text=f'[{str(user_id)}] {inspect.currentframe().f_code.co_name} {str(err)}',
                          severity='error', facility=os.path.basename(__file__))

    async def subscribe(self, user_id: int, full_name: str) -> str:
        """
        Подписаться
        :param user_id: telegram_id пользователя
        :param full_name: полное имя пользователя
        :return: str
        """
        try:
            # если id пользователя не в списке, то регистрируем его
            if user_id not in self.users_id:
                if await self.add({'id': user_id, 'full_name': full_name}):
                    return 'Вы в списке подписчиков, можете работать.'
                else:
                    return 'Добавить вас в список подписчиков у меня не получилось.'
            else:
                return 'Вы уже есть в списке подписчиков'
        except Exception as err:
            await log.log(text=f'[{str(user_id)}] {inspect.currentframe().f_code.co_name} {str(err)}',
                          severity='error', facility=os.path.basename(__file__))

    async def get_all(self) -> str:
        """
        Получить всех пользователей бота
        :return: str
        """
        try:
            # получаем full_name, active всех пользователей из таблицы users с заполненным tg_id
            query = 'SELECT name, active FROM users WHERE tg_id is not NULL'
            subs_users = ''
            subs_count = 0
            unsubs_users = ''
            unsubs_count = 0
            # await db.connect()
            rows = await db.fetch(query=query)
            # await db.disconnect()
            for user in rows:
                if user[1]:
                    subs_count += 1
                    subs_users += f'{subs_count}. {user[0]}\n'
                else:
                    unsubs_count += 1
                    unsubs_users += f'{unsubs_count}. {user[0]}\n'
            return f'Пользователи бота ✔:\n{subs_users}\nПользователи бота ❌:\n{unsubs_users}' if len(
                subs_users + unsubs_users) else 'У бота пока нет пользователей.'
        except Exception as err:
            await log.log(text=f'[no chat_id] {inspect.currentframe().f_code.co_name} {str(err)}', severity='error',
                          facility=os.path.basename(__file__))


reg_users = Users()




