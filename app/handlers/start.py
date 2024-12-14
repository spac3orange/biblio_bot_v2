from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config.logger import logger
from app.config import aiogram_bot
from app.keyboards import main_kb
import os
router = Router()

async def parse_media(path='app/start_image.png'):
    return FSInputFile(path)

@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f'user {message.from_user.username} connected')
    uid = message.from_user.id
    start_photo = await parse_media()
    start_text = '''
Привет! Это 12 Books - твой персональный помощник в невероятном мире историй.
Как и ты, мы очень любим читать, поэтому ежемесячно пополняем нашу библиотеку новыми книгами.
\n\nКак это работает: выбери любую книгу, оформи подписку за донаты и мы доставим ее в удобный пункт выдачи. Книга доступна для аренды в течение 30 календарных дней.
После - ее надо будет вернуть в один из удобных для тебя пунктов. Одновременно ты можешь взять не одну, а несколько книг. В общем, все просто. Начнем? 
    '''
    await message.answer_photo(photo=start_photo, caption=start_text, reply_markup=main_kb.start_btns(uid))


@router.callback_query(F.data == 'back_to_main')
async def p_back_tomain(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    uid = call.from_user.id
    start_photo = await parse_media()
    start_text = '''
Привет! Это 12 Books - твой персональный помощник в невероятном мире историй.
Как и ты, мы очень любим читать, поэтому ежемесячно пополняем нашу библиотеку новыми книгами.
\n\nКак это работает: выбери любую книгу, оформи подписку за донаты и мы доставим ее в удобный пункт выдачи. Книга доступна для аренды в течение 30 календарных дней.
После - ее надо будет вернуть в один из удобных для тебя пунктов. Одновременно ты можешь взять не одну, а несколько книг. В общем, все просто. Начнем? 
    '''
    await call.message.answer_photo(photo=start_photo, caption=start_text, reply_markup=main_kb.start_btns(uid))


@router.message(Command(commands='cancel'))
async def process_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    start_photo = await parse_media()
    start_text = '''
Привет! Это 12 Books - твой персональный помощник в невероятном мире историй.
Как и ты, мы очень любим читать, поэтому ежемесячно пополняем нашу библиотеку новыми книгами.
\n\nКак это работает: выбери любую книгу, оформи подписку за донаты и мы доставим ее в удобный пункт выдачи. Книга доступна для аренды в течение 30 календарных дней.
После - ее надо будет вернуть в один из удобных для тебя пунктов. Одновременно ты можешь взять не одну, а несколько книг. В общем, все просто. Начнем? 
    '''
    await message.answer_photo(photo=start_photo, caption=start_text, reply_markup=main_kb.start_btns(uid))