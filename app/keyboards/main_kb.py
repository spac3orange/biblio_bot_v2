from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardBuilder
from app.config import config_aiogram


def start_btns(user_id):
    kb_builder = InlineKeyboardBuilder()
    admins = config_aiogram.admin_id
    if str(user_id) in admins:
        kb_builder.button(text='Каталог книг', callback_data='books_catalog')
        kb_builder.button(text='Подписка', callback_data='subscription')
        kb_builder.button(text='Личный кабинет', callback_data='user_lk')
        kb_builder.button(text='Корзина', callback_data='cart')
        kb_builder.button(text='Админ панель', callback_data='admin_panel')
    else:
        kb_builder.button(text='Каталог книг', callback_data='books_catalog')
        kb_builder.button(text='Подписка', callback_data='subscription')
        kb_builder.button(text='Личный кабинет', callback_data='user_lk')
        kb_builder.button(text='Корзина', callback_data='cart')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


# Функция для создания Reply-клавиатуры с кнопкой "Корзина"
def get_cart_keyboard():
    # Создаем кнопку "Корзина"
    basket_button = KeyboardButton(text='Корзина')

    # Создаем ReplyKeyboard с одной кнопкой
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(basket_button)

    return keyboard


def catalog_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Соритровка по автору', callback_data='cat_author_sort')
    kb_builder.button(text='Сортировка по жанру', callback_data='cat_janre_sort')
    kb_builder.button(text='Сортировка по теме', callback_data='cat_theme_sort')
    kb_builder.button(text='Поиск по названию', callback_data='cat_name_search')
    kb_builder.button(text='Рекомендации', callback_data='cat_recomendations')
    kb_builder.button(text='Назад', callback_data='back_to_main')

    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def subscription_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Купить подписку', callback_data='buy_sub')
    kb_builder.button(text='Назад', callback_data='back_to_main')

    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def choose_sub_type():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='1 месяц', callback_data='sub_1_month')
    kb_builder.button(text='3 месяца', callback_data='sub_3_months')
    kb_builder.button(text='6 месяцев', callback_data='sub_6_months')
    kb_builder.button(text='12 месяцев', callback_data='sub_12_months')
    kb_builder.button(text='Назад', callback_data='subscription')

    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def admp_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Рекомендации', callback_data='get_recs')
    kb_builder.button(text='Пункты выдачи', callback_data='edit_ppoint')
    kb_builder.button(text='Назад', callback_data='back_to_main')

    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def change_recs():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='add_recs')
    kb_builder.button(text='Удалить', callback_data='add_recs')
    kb_builder.button(text='Назад', callback_data='admin_panel')

    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def lk_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Заполнить данные', callback_data='add_uinfo')
    kb_builder.button(text='Изменить данные', callback_data='change_uinfo')
    kb_builder.button(text='Назад', callback_data='back_to_main')

    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def conf_sub(subtype):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Подтвердить', callback_data='confirm_subtype')
    kb_builder.button(text='Назад', callback_data='buy_sub')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def conf_cdata():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Подтвердить', callback_data='confirm_cdata')
    kb_builder.button(text='Изменить', callback_data='edit_cdata')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def generate_alphabet_buttons():
    kb_builder = InlineKeyboardBuilder()
    alphabet = [chr(i) for i in range(1072, 1104)]  # 'а' (1072) до 'я' (1103)

    for letter in alphabet:
        kb_builder.button(text=letter, callback_data=f'author_{letter}')

    kb_builder.adjust(8)  # Настройка количества кнопок в строке
    return kb_builder.as_markup(resize_keyboard=True)


def cart(book_id):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='В корзину', callback_data=f'add_cart_{book_id}')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def confirm_cart():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Оформить заказ', callback_data=f'confirm_cart')
    kb_builder.button(text='Убрать книгу', callback_data=f'del_from_cart')
    kb_builder.button(text='Очистить корзину', callback_data=f'clear_cart')
    kb_builder.button(text='Главное меню', callback_data=f'back_to_main')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def search_again():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Повторить поиск', callback_data=f'search_again')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)

def edit_ppoints():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить ПВ', callback_data=f'add_ppoint')
    kb_builder.button(text='Удалить ПВ', callback_data=f'del_ppoint')
    kb_builder.button(text='Назад', callback_data=f'admin_panel')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)

def user_edit_ppoints():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Заполнить данные', callback_data=f'add_uinfo')
    kb_builder.button(text='Выбрать пункт выдачи', callback_data=f'user_set_pp')
    kb_builder.button(text='Назад', callback_data=f'back_to_main')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)