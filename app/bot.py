import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import aiogram_bot
from app.config.logger import logger
from app.keyboards import set_commands_menu
from app.handlers import start, books_catalog, subscription, cart, admin_panel, user_lk
from app.crud import db


async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(books_catalog.router)
    dp.include_router(subscription.router)
    dp.include_router(user_lk.router)
    dp.include_router(cart.router)
    dp.include_router(admin_panel.router)

    logger.info('Bot started')

    # Регистрируем меню команд
    await set_commands_menu(aiogram_bot)

    # инициализирем БД
    await db.db_start()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot)


async def main():
    task1 = asyncio.create_task(start_params())
    await asyncio.gather(task1)


if __name__ == '__main__':
    asyncio.run(main())
