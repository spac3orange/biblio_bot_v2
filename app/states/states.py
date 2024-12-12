from aiogram.fsm.state import StatesGroup, State


class InputRecs(StatesGroup):
    input_text = State()


class ContactData(StatesGroup):
    input_name = State()
    input_surname = State()
    input_adress = State()
    comfirm = State()


class DelFromCart(StatesGroup):
    input_id = State()

class NameSearch(StatesGroup):
    input_name = State()

class AddPpoint(StatesGroup):
    input_addr = State()

class DelPpoint(StatesGroup):
    input_addr = State()

class USetPp(StatesGroup):
    input_number = State()