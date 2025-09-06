from aiogram import Router, F
from aiogram.filters import Command

from app.states.calculation_states import CalculationStates
from . import commands, callbacks, messages


def register_handlers(dp):
    """Регистрация всех обработчиков"""
    
    # Команды
    dp.message.register(commands.cmd_start, Command("start"))
    dp.message.register(commands.cmd_help, Command("help"))
    
    # Сообщения с кнопками
    dp.message.register(
        messages.start_calculation, 
        F.text == "📊 Начать расчет"
    )
    dp.message.register(
        messages.new_calculation, 
        F.text == "📊 Новый расчет"
    )
    
    # Обработчики FSM состояний
    dp.message.register(
        messages.process_supplier_code_or_name,
        CalculationStates.waiting_for_supplier_code
    )
    dp.message.register(
        messages.process_year_input,
        CalculationStates.waiting_for_year
    )
    
    # Callback обработчики (порядок важен - от более специфичных к общим)
    dp.callback_query.register(
        callbacks.process_supplier_code_input,
        F.data == "supplier_code_input"
    )
    dp.callback_query.register(
        callbacks.process_month_selection,
        F.data.startswith("month_")
    )
    dp.callback_query.register(
        callbacks.process_supplier_selection,
        lambda c: c.data.startswith("supplier_") and c.data != "supplier_code_input"
    )
    
    # Обработчик неизвестных сообщений (должен быть последним)
    dp.message.register(messages.handle_unknown_message)