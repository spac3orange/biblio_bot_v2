from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config.logger import logger
from app.keyboards import main_kb
from app.config import get_sheet_data
from app.crud import db
from app.states import states
router = Router()


async def process_start(call: CallbackQuery):
    uid = call.from_user.id
    await call.message.answer('Добро пожаловать', reply_markup=main_kb.start_btns(uid))


@router.message(Command(commands='cart'))
async def cart_comm(message: Message, state: FSMContext):
    uid = message.from_user.id
    cart_items = await db.get_cart(uid)
    if cart_items:
        books_str = ''
        gsheet_data = await get_sheet_data()
        for b in cart_items:
            book = next((book for book in gsheet_data if int(book['ID']) == int(b)), None)
            books_str += f'\n\n<b>{book['Автор']}</b>\n{book['Название книги']}\n{book['Год выпуска']}\n<b>id: {book['ID']}</b>'
        await message.answer(books_str, reply_markup=main_kb.confirm_cart(), parse_mode='HTML')

    else:
        await message.answer('В корзине пусто.')


@router.callback_query(F.data == 'cart')
async def p_cart(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    cart_items = await db.get_cart(uid)
    if cart_items:
        books_str = ''
        gsheet_data = await get_sheet_data()
        for b in cart_items:
            book = next((book for book in gsheet_data if int(book['ID']) == int(b)), None)
            books_str += f'\n\n<b>{book['Автор']}</b>\n{book['Название книги']}\n{book['Год выпуска']}\n<b>id: {book['ID']}</b>'
        await call.message.answer(books_str, reply_markup=main_kb.confirm_cart(), parse_mode='HTML')

    else:
        await call.message.answer('В корзине пусто.')


@router.callback_query(F.data.startswith('add_cart_'))
async def p_addtocart(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    book_id = call.data.split('_')[-1]
    await db.add_to_cart(uid, int(book_id))
    await call.message.answer('Книга добавлена в корзину')


@router.callback_query(F.data == 'clear_cart')
async def p_c_cart(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    await db.clear_cart(uid)
    await call.message.answer('Корзина очищена.')
    await process_start(call)


@router.callback_query(F.data == 'del_from_cart')
async def p_del_f_cart(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите ID книги, которую вы хотите удалить из корзины: \nОтменить /cancel')
    await state.set_state(states.DelFromCart.input_id)


@router.message(states.DelFromCart.input_id)
async def p_input_bid(message: Message, state: FSMContext):
    book_id = message.text
    uid = message.from_user.id
    await db.remove_from_cart(uid, int(book_id))
    await message.answer('Книга удалена из корзины.')
    await state.clear()
    await cart_comm(message, state)
