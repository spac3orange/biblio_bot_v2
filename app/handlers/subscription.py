from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config.logger import logger
from app.keyboards import main_kb
from app.crud import db
router = Router()


@router.callback_query(F.data == 'subscription')
async def p_subscription(call: CallbackQuery):
    await call.answer()
    uid = call.from_user.id
    sub = await db.get_subscription(uid)
    print(sub)
    sub_text = '''
    Подписка помогает нам расширять нашу библиотеку, улучшать сервис и делать так, чтобы больше людей каждый день могли получать удовольствие от чтения. 
    Чтобы получить доступ к библиотеке, выбери один из вариантов подписки - в рамках 30 дней ты можешь взять в аренду 1 или несколько книг. Продлевать аренду, к сожалению, нельзя.
    '''
    await call.message.answer(text=sub_text + f'\n\nСтатус подписки: {sub}'
                              f'\nДата начала подписки: '
                              f'\nДата окончания подписки: ', reply_markup=main_kb.subscription_menu())


@router.callback_query(F.data == 'buy_sub')
async def p_buy_sub(call: CallbackQuery):
    await call.answer()
    await call.message.answer('Выберите тип подписки: ', reply_markup=main_kb.choose_sub_type())


@router.callback_query(F.data.startswith('sub_'))
async def p_sublength(call: CallbackQuery):
    await call.answer()
    cdata = call.data.split('_')
    subtype = cdata[-2]
    await call.message.answer(f'Выбрана подписка: {subtype} месяц'
                              f'\nСтоимость: None', reply_markup=main_kb.conf_sub(subtype))
