from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config.logger import logger
from app.states import states
from app.keyboards import main_kb
from app.config import get_sheet_data
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from app.crud import db
router = Router()


@router.callback_query(F.data == 'books_catalog')
async def p_bcat(call: CallbackQuery):
    await call.answer()
    catalog_text = '''
Здесь собраны все наши книги, которые ждут встречи с тобой прямо сейчас.
Если книга не кликабельна, значит ее сейчас кто-то читает, но совсем скоро она снова будет доступна
    '''
    await call.message.answer(text=catalog_text, reply_markup=main_kb.catalog_menu())


@router.callback_query(F.data == 'cat_author_sort')
async def send_author_buttons(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Выберите первую букву автора:", reply_markup=main_kb.generate_alphabet_buttons())


@router.callback_query(F.data.startswith('author_'))
async def p_authorsort(call: CallbackQuery):
    a_letter = call.data.split('_')[-1]
    gsheet_data = await get_sheet_data()

    # Собираем уникальные фамилии авторов
    authors = set()
    for book in gsheet_data:
        author_lastname = book['Автор'].split()[0]  # Берем только фамилию автора
        if author_lastname[0].lower() == a_letter.lower():  # Сортируем по первой букве фамилии
            authors.add(author_lastname)

    # Создаем Inline-клавиатуру с фамилиями авторов через InlineKeyboardBuilder
    keyboard_builder = InlineKeyboardBuilder()
    for author in sorted(authors):
        keyboard_builder.add(
            InlineKeyboardButton(text=author, callback_data=f"selected_author_{author}")
        )
    keyboard_builder.button(text='Назад', callback_data='cat_author_sort')
    # Создаем клавиатуру с 1 кнопкой в ряд
    keyboard_builder.adjust(1)
    keyboard = keyboard_builder.as_markup(resize_keyboard=True)

    # Отправляем сообщение с клавиатурой
    if authors:
        await call.message.answer("Выберите автора:", reply_markup=keyboard)
    else:
        await call.message.answer("Авторы с такой буквой не найдены.")


@router.callback_query(F.data.startswith('selected_author_'))
async def p_selected_auth(call: CallbackQuery):
    await call.answer()
    author_surname = call.data.split('_')[-1]
    gsheet_data = await get_sheet_data()

    # Фильтруем книги по фамилии автора
    books_by_author = [book for book in gsheet_data if book['Автор'].split()[0] == author_surname]

    # Если книги найдены, выводим информацию по каждой книге
    if books_by_author:
        for book in books_by_author:
            await call.message.answer(
                f"\n<b>Автор:</b> {book['Автор']}\n<b>Название:</b> {book['Название книги']}"
                f"\n<b>Год:</b> {book['Год выпуска']}\n<b>Аннотация:</b> {book['Аннотация ']}",
                parse_mode='HTML',
                reply_markup=main_kb.cart(book['ID'])
            )
    else:
        await call.message.answer(f"Книги автора {author_surname} не найдены.")


@router.callback_query(F.data == 'cat_janre_sort')
async def p_janre_sort(call: CallbackQuery):
    await call.answer()
    # Создаем Inline-клавиатуру с фамилиями авторов через InlineKeyboardBuilder
    gsheet_data = await get_sheet_data()
    janres = set([book['Жанр'] for book in gsheet_data])
    keyboard_builder = InlineKeyboardBuilder()
    for j in sorted(janres):
        keyboard_builder.add(
            InlineKeyboardButton(text=j, callback_data=f"selected_janre_{j}")
        )
    keyboard_builder.button(text='Назад', callback_data='cat_author_sort')
    # Создаем клавиатуру с 1 кнопкой в ряд
    keyboard_builder.adjust(1)
    keyboard = keyboard_builder.as_markup(resize_keyboard=True)
    await call.message.answer('Выберите жанр:', reply_markup=keyboard)


@router.callback_query(F.data.startswith('selected_janre_'))
async def p_sel_janre(call: CallbackQuery):
    await call.answer()
    janre = call.data.split('_')[-1]
    gsheet_data = await get_sheet_data()

    # Формируем список книг в формате 'Автор - Название книги'
    books = [{'id': book['ID'], 'info': f"{book['Автор']} - {book['Название книги']}"} for book in gsheet_data if book['Жанр'] == janre]

    print(books)  # Пример: [{'id': '123', 'info': 'Маннара Франко - Меня зовут Бёрди'}, ...]

    keyboard_builder = InlineKeyboardBuilder()

    # Итерация по книгам
    for book in sorted(books, key=lambda x: x['info']):
        book_info = book['info']
        book_id = book['id']

        # Формируем callback_data с уникальным идентификатором книги
        print(f"Book: {book_info}, ID: {book_id}")
        keyboard_builder.add(
            InlineKeyboardButton(text=book_info, callback_data=f"sjb_{book_id}")
        )

    # Добавляем кнопку "Назад"
    keyboard_builder.button(text='Назад', callback_data='cat_janre_sort')

    # Создаем клавиатуру с 1 кнопкой в ряд
    keyboard_builder.adjust(1)
    keyboard = keyboard_builder.as_markup(resize_keyboard=True)

    # Отправляем сообщение с клавиатурой
    await call.message.answer('Выберите книгу:', reply_markup=keyboard)


@router.callback_query(F.data == 'cat_theme_sort')
async def p_sel_theme(call: CallbackQuery):
    await call.message.answer('В разработке.')

@router.callback_query(F.data == 'cat_name_search')
async def p_cat_search(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите название книги: ')
    await state.set_state(states.NameSearch.input_name)


@router.message(states.NameSearch.input_name)
async def p_search_book(message: Message, state: FSMContext):
    name = message.text.strip().lower()  # Получаем название книги из сообщения и приводим к нижнему регистру для поиска
    await state.clear()
    # Отправляем сообщение, что поиск начался
    msg = await message.answer(f'Идет поиск книги "{name}"...')

    # Получаем данные из Google Таблицы
    gsheet_data = await get_sheet_data()

    # Формируем список книг, фильтруя по жанру и названию
    filtered_books = [
        {
            'id': book['ID'],
            'info': (
                f"<b>Автор:</b> {book['Автор']}\n"
                f"<b>Название:</b> {book['Название книги']}\n"
                f"<b>Год выпуска:</b> {book['Год выпуска']}\n"
                f"<b>Аннотация:</b> {book['Аннотация ']}"
            )
        }
        for book in gsheet_data
        if name in book['Название книги'].strip().lower()
    ]
    # Если книги не найдены
    if not filtered_books:
        await msg.edit_text(f'Книги с названием "{name}" не найдены.', reply_markup=main_kb.search_again())
    else:
        for book in filtered_books:
            print(book)
            await msg.edit_text(
                f"{book['info']}",
                parse_mode='HTML',
                reply_markup=main_kb.cart(book['id'])  # Кнопка "Добавить в корзину"
            )

@router.callback_query(F.data == 'search_again')
async def p_sagain(call: CallbackQuery, state: FSMContext):
    await p_cat_search(call, state)


@router.callback_query(F.data.startswith('sjb_'))
async def p_sel_j_book(call: CallbackQuery):
    await call.answer()
    # Извлекаем идентификатор книги из callback_data
    book_id = call.data.split('_')[-1]
    print(book_id)
    # Получаем данные с Google Sheets
    gsheet_data = await get_sheet_data()

    # Ищем книгу по ID
    book = next((book for book in gsheet_data if int(book['ID']) == int(book_id)), None)

    # Проверка, что книга найдена
    if book:
        # Формируем сообщение с данными о книге
        await call.message.answer(
            f"\n<b>Автор:</b> {book['Автор']}\n<b>Название:</b> {book['Название книги']}"
            f"\n<b>Год:</b> {book['Год выпуска']}\n<b>Аннотация:</b> {book['Аннотация ']}",
            parse_mode='HTML',
            reply_markup=main_kb.cart(book['ID'])  # Здесь вы создаете клавиатуру для действия с книгой (например, добавить в корзину)
        )
    else:
        # Если книга не найдена, отправляем сообщение об ошибке
        await call.message.answer("Книга не найдена, попробуйте снова.")


@router.callback_query(F.data == 'cat_recomendations')
async def p_cat_recs(call: CallbackQuery):
    await call.answer()
    recs = await db.fetch_recs()
    gsheet_data = await get_sheet_data()
    for r in recs:
        r = r['recs_id']
        # Ищем книгу по ID
        book = next((book for book in gsheet_data if int(book['ID']) == int(r)), None)
        if book:
            await call.message.answer(
                f"\n<b>Автор:</b> {book['Автор']}\n<b>Название:</b> {book['Название книги']}"
                f"\n<b>Год:</b> {book['Год выпуска']}\n<b>Аннотация:</b> {book['Аннотация ']}",
                parse_mode='HTML',
                reply_markup=main_kb.cart(book['ID'])  # Здесь вы создаете клавиатуру для действия с книгой (например, добавить в корзину)
            )

        print(book)
    print(recs)
    pass
