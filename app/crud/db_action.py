import asyncpg
from environs import Env
from app.config import logger
from typing import List, Dict, Tuple
import asyncio


class Database:
    def __init__(self):
        (self.user, self.password,
         self.host, self.db_name, self.db_port) = self.parse_env()
        self.pool = None

    @staticmethod
    def parse_env():
        env = Env()
        # env.read_env(path=path)
        user = env('DB_USER')
        password = env('DB_PASSWORD')
        host = env('DB_HOST')
        db_name = env('DB_NAME')
        db_port = env('DB_PORT')
        return user, password, host, db_name, db_port

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                host=self.host,
                database=self.db_name,
                port=self.db_port,
                min_size=20,
                max_size=100,
            )

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while creating connection pool", error)
            print(error)

    async def close_pool(self):
        if self.pool:
            await self.pool.close()

    async def execute_query(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while executing query", error)

    async def fetch_row(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while fetching row", error)

    async def fetch_all(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while fetching all", error)

    async def db_start(self) -> None:
        try:
            await self.create_pool()

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    user_name TEXT
                )
            """)

            await self.execute_query("""
                            CREATE TABLE IF NOT EXISTS subscriptions (
                                user_id BIGINT PRIMARY KEY,
                                user_name TEXT,
                                sub_type TEXT DEFAULT 'None',
                                sub_start_date TEXT DEFAULT 'None',
                                sub_end_date TEXT DEFAULT 'None'
                            )
                        """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS recomendations (
                    user_id BIGINT,
                    recs_id INT,
                    PRIMARY KEY (user_id, recs_id)
                )
            """)

            await self.execute_query("""
                            CREATE TABLE IF NOT EXISTS ppoints (
                                address TEXT
                            )
                        """)

            await self.execute_query("""
                            CREATE TABLE IF NOT EXISTS contact_data (
                                user_id BIGINT PRIMARY KEY,
                                name TEXT,
                                SURNAME TEXT,
                                ppoint TEXT
                            )
                        """)

            await self.execute_query("""
                            CREATE TABLE IF NOT EXISTS cart (
                                user_id BIGINT,
                                book_id BIGINT,
                                PRIMARY KEY (user_id, book_id)
                            )
                            """)

            logger.info('Database started')

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while connecting to DB", error)

    async def fetch_recs(self) -> str:
        try:
            query = "SELECT * from recomendations"
            recs = await self.fetch_all(query)
            return recs

        except (Exception, asyncpg.PostgresError) as error:
            logger.error('Error while fetching recomendations', error)

    async def fetch_ppoints(self) -> str:
        try:
            query = "SELECT * from ppoints"
            ppoints = await self.fetch_all(query)
            return ppoints

        except (Exception, asyncpg.PostgresError) as error:
            logger.error('Error while fetching ppoints', error)

    async def add_ppoint(self, address: str) -> None:
        try:
            # Добавляем пункт выдачи
            query = "INSERT INTO ppoints (address) VALUES ($1)"
            await self.execute_query(query, address)
            logger.info(f"Address '{address}' added to ppoints.")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f'Error while adding address {address} to ppoints', error)

    async def remove_ppoint(self, address: str) -> None:
        try:
            # Удаляем пункт выдачи
            query = "DELETE FROM ppoints WHERE address = $1"
            result = await self.execute_query(query, address)

            if result:
                logger.info(f"Address '{address}' removed from ppoints.")
            else:
                logger.warning(f"Address '{address}' not found in ppoints.")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f'Error while removing address {address} from ppoints', error)

    async def update_recs(self, user_id: int, recs_id: int) -> None:
        print(user_id, recs_id)
        try:
            query = """
                UPDATE recomendations
                SET recs_id = $2
                WHERE user_id = $1
            """
            # Выполнение запроса
            await self.execute_query(query, user_id, recs_id)
            logger.info(f"Updated recs_text for user_id {user_id}")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while updating recs_text for user_id {user_id}", error)

    async def insert_recs(self, user_id: int, recs_id: int) -> None:
        print(user_id, recs_id)
        try:
            query = """
                INSERT INTO recomendations (user_id, recs_id)
                VALUES ($1, $2)
            """
            # Выполнение запроса
            await self.execute_query(query, user_id, recs_id)
            logger.info(f"Inserted or updated recs for user_id {user_id}")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while inserting recs for user_id {user_id}", error)

    async def insert_contact_data(self, user_id: int, ppoint: str) -> None:
        try:
            # Формируем SQL-запрос на вставку данных в таблицу contact_data
            query = """
            INSERT INTO contact_data (user_id, ppoint)
            VALUES ($1, $2)
            ON CONFLICT (user_id) 
            DO UPDATE SET ppoint = EXCLUDED.ppoint
            """
            # Выполняем запрос к базе данных
            await self.execute_query(query, user_id, ppoint)
            logger.info(f"Data for user_id {user_id} inserted/updated successfully")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while inserting data into contact_data for user_id {user_id}: {error}")

    async def insert_fio(self, user_id: int, name: str, surname: str) -> None:
        try:
            # Формируем SQL-запрос на вставку данных в таблицу contact_data
            query = """
            INSERT INTO contact_data (user_id, name, surname)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
            name = EXCLUDED.name,
            surname = EXCLUDED.surname
        """
            # Выполняем запрос к базе данных
            await self.execute_query(query, user_id, name, surname)
            logger.info(f"Data for user_id {user_id} inserted/updated successfully")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while inserting data into contact_data for user_id {user_id}: {error}")

    async def get_fio(self, user_id: int) -> dict:
        try:
            # SQL-запрос для получения имени и фамилии по user_id
            query = """
            SELECT name, surname
            FROM contact_data
            WHERE user_id = $1
            """
            # Выполняем запрос и получаем результат
            result = await self.fetch_row(query, user_id)

            # Если данные найдены, возвращаем их в виде словаря
            if result:
                return {
                    "name": result["name"],
                    "surname": result["surname"]
                }
            else:
                logger.info(f"No FIO data found for user_id {user_id}")
                return None

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while fetching FIO for user_id {user_id}: {error}")
            return None

    async def get_contact_data_by_user_id(self, user_id: int) -> dict:
        try:
            # SQL-запрос для получения данных по user_id
            query = """
            SELECT user_id, ppoint
            FROM contact_data
            WHERE user_id = $1
            """
            # Выполняем запрос и получаем результат
            result = await self.fetch_row(query, user_id)

            # Если данные найдены, возвращаем их в виде словаря
            if result:
                return {
                    "user_id": result["user_id"],
                    "ppoint": result["ppoint"]
                }
            else:
                logger.info(f"No data found for user_id {user_id}")
                return None

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while fetching data for user_id {user_id}: {error}")
            return None

    async def add_to_cart(self, user_id: int, book_id: int) -> None:
        try:
            # SQL-запрос для вставки записи в таблицу cart
            query = """
            INSERT INTO cart (user_id, book_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING;
            """
            # Выполняем запрос к базе данных
            await self.execute_query(query, user_id, book_id)
            logger.info(f"Book with ID {book_id} added to cart for user {user_id} successfully")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while adding book {book_id} to cart for user {user_id}: {error}")

    async def get_cart(self, user_id: int) -> list:
        try:
            # SQL-запрос для получения всех записей для данного пользователя
            query = """
            SELECT book_id
            FROM cart
            WHERE user_id = $1;
            """
            # Выполняем запрос и получаем результат
            rows = await self.fetch_all(query, user_id)

            # Преобразуем результат в список book_id
            cart_items = [row['book_id'] for row in rows]

            logger.info(f"Cart retrieved for user {user_id}, contains {len(cart_items)} items")

            return cart_items

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while retrieving cart for user {user_id}: {error}")
            return []

    async def clear_cart(self, user_id: int) -> None:
        try:
            # SQL-запрос для удаления всех записей для данного пользователя
            query = """
            DELETE FROM cart
            WHERE user_id = $1;
            """
            # Выполняем запрос к базе данных
            await self.execute_query(query, user_id)
            logger.info(f"All items for user {user_id} removed from cart successfully")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while clearing cart for user {user_id}: {error}")

    async def remove_from_cart(self, user_id: int, book_id: int) -> None:
        try:
            # SQL-запрос для удаления конкретной записи из таблицы cart
            query = """
            DELETE FROM cart
            WHERE user_id = $1 AND book_id = $2;
            """
            # Выполняем запрос к базе данных
            await self.execute_query(query, user_id, book_id)
            logger.info(f"Book with ID {book_id} removed from cart for user {user_id} successfully")

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while removing book {book_id} from cart for user {user_id}: {error}")

    async def get_subscription(self, user_id: int) -> tuple | None:
        try:
            # SQL-запрос для получения данных подписки пользователя
            query = """
            SELECT sub_type, sub_start_date, sub_end_date
            FROM subscriptions
            WHERE user_id = $1;
            """
            # Выполняем запрос к базе данных и получаем результат
            row = await self.fetch_row(query, user_id)

            # Проверяем наличие данных и значение sub_type
            if row and row['sub_type'] != 'None':
                return row['sub_type'], row['sub_start_date'], row['sub_end_date']
            else:
                return None

        except (Exception, asyncpg.PostgresError) as error:
            logger.error(f"Error while fetching subscription for user {user_id}: {error}")
            return None


db = Database()


