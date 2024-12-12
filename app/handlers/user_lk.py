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
router = Router()

async def m_user_lk(message: Message):
    uid = message.from_user.id
    ppoint = await db.get_contact_data_by_user_id(uid)
    fio = await db.get_fio(uid)
    fio = f'{fio['name']} {fio['surname']}' if fio else None
    if ppoint:
        await message.answer(f'<b>ФИО:</b> {fio}'
                             f'\n<b>Пункт выдачи:</b> {ppoint['ppoint']}', reply_markup=main_kb.user_edit_ppoints(), parse_mode='HTML')
    else:
        await message.answer(f'<b>ФИО:</b> {fio}'
                             '\n<b>Пункт выдачи:</b> Не выбран', reply_markup=main_kb.user_edit_ppoints(), parse_mode='HTML')

@router.callback_query(F.data == 'user_lk')
async def p_userlk(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    ppoint = await db.get_contact_data_by_user_id(uid)
    fio = await db.get_fio(uid)
    fio = f'{fio['name']} {fio['surname']}' if fio else None
    if ppoint:
        await call.message.answer(f'<b>ФИО:</b> {fio}'
                                  f'\n<b>Пункт выдачи:</b> {ppoint['ppoint']}', reply_markup=main_kb.user_edit_ppoints(), parse_mode='HTML')
    else:
        await call.message.answer(f'<b>ФИО:</b> {fio}'
                                  '\n<b>Пункт выдачи:</b> Не выбран', reply_markup=main_kb.user_edit_ppoints(), parse_mode='HTML')

@router.callback_query(F.data == 'user_set_pp')
async def user_set_pp(call: CallbackQuery, state: FSMContext):
    ppoints = await db.fetch_ppoints()
    # Формируем строку с пунктами выдачи, пронумерованными и без "Record address"
    ppoints_list = "\n".join([f"{i + 1}. {ppoint['address']}" for i, ppoint in enumerate(ppoints)])
    await call.message.answer(f'Введите номер пункта выдачи: \n{ppoints_list}\nОтменить - /cancel')
    await state.set_state(states.USetPp.input_number)

@router.message(states.USetPp.input_number)
async def pp_updated(message: Message, state: FSMContext):
    ppoint_number = int(message.text)-1
    uid = message.from_user.id
    ppoints = await db.fetch_ppoints()
    addresses = [record["address"] for record in ppoints]
    await db.insert_contact_data(uid, addresses[ppoint_number])
    await state.clear()
    await message.answer('Пункт выдачи обновлён.')
    await m_user_lk(message)


#     cdata = await db.get_contact_data_by_user_id(uid)
#     if cdata:
#         str_data = f'<b>ФИО:</b> {cdata['name']} {cdata['surname']}\n<b>Адрес:</b> {cdata['address']}'
#     else:
#         str_data = 'Данные не указаны. Пожалуйста, заполните контактные данные.'
#     await call.message.answer(text=str_data, reply_markup=main_kb.lk_menu(), parse_mode='HTML')
#
#
@router.callback_query(F.data == 'add_uinfo')
async def p_changeuinfo(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите ваше имя: \nОтменить /cancel')
    await state.set_state(states.ContactData.input_name)


@router.message(states.ContactData.input_name)
async def p_input_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer('Введите фамилию:\nОтменить /cancel')
    await state.set_state(states.ContactData.input_surname)


@router.message(states.ContactData.input_surname)
async def p_input_surname(message: Message, state: FSMContext):
    surname = message.text
    uid = message.from_user.id
    await state.update_data(surname=surname)
    sdata = await state.get_data()
    await db.insert_fio(uid, sdata['name'], sdata['surname'])
    await message.answer('Данные обновлены.')
    await m_user_lk(message)
#
#
# @router.message(states.ContactData.input_adress)
# async def p_input_adress(message: Message, state: FSMContext):
#     adress = message.text
#     await state.update_data(adress=adress)
#     sdata = await state.get_data()
#     await message.answer(f'Имя: {sdata['name']}\nФамилия: {sdata['surname']}\nАдрес: {sdata['adress']}',
#                          reply_markup=main_kb.conf_cdata())
#     await state.set_state(states.ContactData.comfirm)
#
#
# @router.callback_query(F.data == 'confirm_cdata')
# async def p_conf_cdata(call: CallbackQuery, state: FSMContext):
#     await call.answer()
#     uid = call.from_user.id
#     username = call.from_user.username
#     sdata = await state.get_data()
#     print(sdata)
#     await db.insert_contact_data(uid, username, sdata['name'], sdata['surname'], sdata['adress'])
#     await state.clear()
#     await call.message.answer('Данные сохранены.')
#     await p_userlk(call)
#
#
# @router.callback_query(F.data == 'edit_cdata')
# async def p_edit_cdata(call: CallbackQuery, state: FSMContext):
#     await call.answer()
#     await state.clear()
#     await p_changeuinfo(call, state=state)
#
#
# @router.callback_query(F.data == 'change_uinfo')
# async def p_edit_cdata(call: CallbackQuery, state: FSMContext):
#     await call.answer()
#     await state.clear()
#     await p_changeuinfo(call, state=state)

