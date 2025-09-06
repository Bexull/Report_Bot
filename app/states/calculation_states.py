from aiogram.fsm.state import State, StatesGroup


class CalculationStates(StatesGroup):
    """Состояния FSM для процесса расчета часов поставщиков"""
    waiting_for_supplier = State()
    waiting_for_supplier_code = State()
    waiting_for_year = State()
    waiting_for_month = State()