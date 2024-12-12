from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from pyasn1_modules.rfc7906 import aa_keyWrapAlgorithm

from app.config.logger import logger
from app.keyboards import main_kb
from app.filters import IsAdmin
from app.crud import db
from app.states import states
from app.config import get_sheet_data
router = Router()
router.message.filter(
    IsAdmin(F)
)


async def send_ppoints(message: Message):
    ppoints = await db.fetch_ppoints()
    # Формируем строку с пунктами выдачи, пронумерованными и без "Record address"
    ppoints_list = "\n".join([f"{i + 1}. {ppoint['address']}" for i, ppoint in enumerate(ppoints)])

    # Если пункты выдачи найдены, отправляем сообщение
    if ppoints_list:
        await message.answer(f"Пункты выдачи:\n{ppoints_list}", reply_markup=main_kb.edit_ppoints())
    else:
        await message.answer("Пункты выдачи не найдены.", reply_markup=main_kb.edit_ppoints())


async def grecs_msg(message: Message):
    uid = message.from_user.id
    current_recs = await db.fetch_recs()
    gsheet_data = await get_sheet_data()
    recs_str = ''
    for r in current_recs:
        r = r['recs_id']
        book = next((book for book in gsheet_data if int(book['ID']) == int(r)), None)
        recs_str += f'\n<b>ID: {book['ID']}</b> {book['Автор']} - {book['Название книги']}'
    link = '<a href="https://docs.google.com/spreadsheets/d/1U7al_0wu9BuxBOwqs0ASMdNf_PyQfc70gXA4w2rulH0/edit?gid=0#gid=0">Полная таблица с книгами</a>'
    await message.answer(f'{link}'
                         f'\nРекомендации: \n{recs_str}', reply_markup=main_kb.change_recs(), parse_mode='HTML')


@router.callback_query(F.data == 'admin_panel')
async def p_admin_panel(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Админ панель', reply_markup=main_kb.admp_menu())


@router.callback_query(F.data == 'get_recs')
async def p_grecs(call: CallbackQuery):
    uid = call.from_user.id
    current_recs = await db.fetch_recs()
    gsheet_data = await get_sheet_data()
    recs_str = ''
    for r in current_recs:
        r = r['recs_id']
        book = next((book for book in gsheet_data if int(book['ID']) == int(r)), None)
        recs_str += f'\n<b>ID: {book['ID']}</b> {book['Автор']} - {book['Название книги']}'
    await call.answer()
    link = '<a href="https://docs.google.com/spreadsheets/d/1U7al_0wu9BuxBOwqs0ASMdNf_PyQfc70gXA4w2rulH0/edit?gid=0#gid=0">Полная таблица с книгами</a>'
    await call.message.answer(f'{link}'
                              f'\nРекомендации: \n{recs_str}', reply_markup=main_kb.change_recs(), parse_mode='HTML')


@router.callback_query(F.data == 'add_recs')
async def p_chrecs(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите ID книги:')
    await state.set_state(states.InputRecs.input_text)


@router.message(states.InputRecs.input_text)
async def p_input_recs(message: Message, state: FSMContext):
    uid = message.from_user.id
    gsheet_data = await get_sheet_data()
    new_recs = int(message.text)
    print(len(gsheet_data))
    if new_recs > len(gsheet_data):
        await message.answer('Ошибка. Такого ID не существует.\nВведите новый ID:\nОтменить - /cancel')
    else:
        print(new_recs)
        await db.insert_recs(uid, new_recs)
        logger.info('recomendations updated')
        await message.answer('Книга добавлена в рекомендации.')
        await state.clear()
        await grecs_msg(message)


@router.callback_query(F.data == 'edit_ppoint')
async def p_edit_ppoint(call: CallbackQuery):
    await call.answer()
    ppoints = await db.fetch_ppoints()
    # Формируем строку с пунктами выдачи, пронумерованными и без "Record address"
    ppoints_list = "\n".join([f"{i + 1}. {ppoint['address']}" for i, ppoint in enumerate(ppoints)])

    # Если пункты выдачи найдены, отправляем сообщение
    if ppoints_list:
        await call.message.answer(f"Пункты выдачи:\n{ppoints_list}", reply_markup=main_kb.edit_ppoints())
    else:
        await call.message.answer("Пункты выдачи не найдены.", reply_markup=main_kb.edit_ppoints())


@router.callback_query(F.data == 'add_ppoint')
async def p_add_ppoint(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите адрес пункта выдачи: ')
    await state.set_state(states.AddPpoint.input_addr)


@router.message(states.AddPpoint.input_addr)
async def p_conf_add_pp(message: Message, state: FSMContext):
    ppoint = message.text
    await db.add_ppoint(ppoint)
    await state.clear()
    await message.answer('Пункт выдачи добавлен.')
    await send_ppoints(message)


@router.callback_query(F.data == 'del_ppoint')
async def p_del_ppoint(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите адрес пункта выдачи: ')
    await state.set_state(states.DelPpoint.input_addr)


@router.message(states.DelPpoint.input_addr)
async def p_conf_del_pp(message: Message, state: FSMContext):
    ppoint = message.text
    try:
        await db.remove_ppoint(ppoint)
        await message.answer('Пункт выдачи удален.')
        await state.clear()
        await send_ppoints(message)
    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при удалении пункта выдачи.')
        await state.clear()
        await send_ppoints(message)

