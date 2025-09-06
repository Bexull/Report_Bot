import calendar
from datetime import date
from aiogram import types
from aiogram.fsm.context import FSMContext

from app.states.calculation_states import CalculationStates
from app.services.calculation import CalculationService
from app.keyboards.reply import ReplyKeyboards
from app.config.settings import MONTH_NAMES


async def process_supplier_code_input(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка запроса на ввод кода поставщика"""
    await callback_query.message.edit_text(
        "🔢 Введите код поставщика (например, 1064):\n\n"
        "Или введите полное название компании:"
    )
    
    await state.set_state(CalculationStates.waiting_for_supplier_code)
    await callback_query.answer()


async def process_supplier_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора поставщика"""
    supplier_index = int(callback_query.data.split("_")[1])
    
    # Получаем данные из состояния
    data = await state.get_data()
    suppliers = data.get("suppliers", [])
    
    if supplier_index >= len(suppliers):
        await callback_query.answer("❌ Неверный индекс поставщика")
        return
    
    selected_supplier = suppliers[supplier_index]
    
    # Сохраняем выбранного поставщика
    await state.update_data(selected_supplier=selected_supplier)
    
    await callback_query.message.edit_text(
        f"✅ Выбран поставщик: {selected_supplier}\n\n"
        "📅 Теперь введите год для анализа (например, 2025):"
    )
    
    await state.set_state(CalculationStates.waiting_for_year)
    await callback_query.answer()


async def process_month_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора месяца и выполнение расчета"""
    month = int(callback_query.data.split("_")[1])
    
    # Получаем данные из состояния
    data = await state.get_data()
    supplier_name = data.get("selected_supplier")
    year = data.get("year")
    
    if not supplier_name or not year:
        await callback_query.answer("❌ Ошибка: данные не найдены")
        return
    
    # Формируем даты
    start_date = date(year, month, 1)
    _, days_in_month = calendar.monthrange(year, month)
    end_date = date(year, month, days_in_month)
    
    await callback_query.message.edit_text(
        f"🔄 Выполняю расчет для:\n"
        f"🏢 Поставщик: {supplier_name}\n"
        f"📅 Период: {MONTH_NAMES[month-1].title()} {year}\n"
        f"📅 Даты: {start_date} - {end_date}\n\n"
        f"⏳ Подождите, получаю данные..."
    )
    
    # Выполняем расчет
    result = await CalculationService.perform_calculation(supplier_name, start_date, end_date)
    
    # Отправляем результат
    await callback_query.message.edit_text(result, parse_mode="HTML")
    
    # Сбрасываем состояние
    await state.clear()
    
    # Показываем кнопку для нового расчета
    keyboard = ReplyKeyboards.get_new_calculation_menu()
    
    await callback_query.message.answer(
        "🔄 Хотите выполнить новый расчет?",
        reply_markup=keyboard
    )
    
    await callback_query.answer()