from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config.logger import logger
from app.config import aiogram_bot
from app.keyboards import main_kb
import os
router = Router()

async def parse_media(path='start_image.png'):
    return FSInputFile(path)

@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f'user {message.from_user.username} connected')
    uid = message.from_user.id
    start_photo = await parse_media()
    await message.answer_photo(photo=start_photo, caption='Добро пожаловать', reply_markup=main_kb.start_btns(uid))


@router.callback_query(F.data == 'back_to_main')
async def p_back_tomain(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    uid = call.from_user.id
    start_photo = await parse_media()
    await call.message.answer_photo(photo=start_photo, caption='Добро пожаловать', reply_markup=main_kb.start_btns(uid))


@router.message(Command(commands='cancel'))
async def process_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    start_photo = await parse_media()
    await message.answer_photo(photo=start_photo, caption='Добро пожаловать', reply_markup=main_kb.start_btns(uid))