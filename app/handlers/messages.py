from aiogram import types
from aiogram.fsm.context import FSMContext

from app.states.calculation_states import CalculationStates
from app.services.database import DatabaseService
from app.keyboards.inline import InlineKeyboards
from app.config.settings import YEAR_RANGE_MIN, YEAR_RANGE_MAX


async def start_calculation(message: types.Message, state: FSMContext):
    """Начало процесса расчета"""
    connection = DatabaseService.connect_to_database()
    if connection is None:
        await message.answer("❌ Ошибка подключения к базе данных. Попробуйте позже.")
        return
    
    try:
        suppliers = DatabaseService.get_available_suppliers(connection)
        if not suppliers:
            await message.answer("❌ Не найдено поставщиков в базе данных.")
            connection.close()
            return
        
        # Сохраняем список поставщиков в состоянии
        await state.update_data(suppliers=suppliers)
        
        # Создаем клавиатуру с поставщиками
        keyboard = InlineKeyboards.create_suppliers_keyboard(suppliers)
        
        await message.answer(
            f"🏢 Выберите поставщика для анализа:\n\nНайдено {len(suppliers)} поставщиков\n\n"
            "Или нажмите '🔢 Ввести код поставщика' если знаете код",
            reply_markup=keyboard
        )
        
        await state.set_state(CalculationStates.waiting_for_supplier)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        connection.close()


async def new_calculation(message: types.Message, state: FSMContext):
    """Начало нового расчета"""
    # Сбрасываем состояние перед новым расчетом
    await state.clear()
    await start_calculation(message, state)


async def process_supplier_code_or_name(message: types.Message, state: FSMContext):
    """Обработка ввода кода или названия поставщика"""
    user_input = message.text.strip()
    
    if not user_input:
        await message.answer("❌ Введите код или название поставщика:")
        return
    
    connection = DatabaseService.connect_to_database()
    if connection is None:
        await message.answer("❌ Ошибка подключения к базе данных. Попробуйте позже.")
        return
    
    try:
        # Пытаемся найти поставщика по коду или названию
        supplier = DatabaseService.find_supplier_by_code_or_name(connection, user_input)
        
        if supplier:
            # Сохраняем выбранного поставщика
            await state.update_data(selected_supplier=supplier)
            
            await message.answer(
                f"✅ Выбран поставщик: {supplier}\n\n"
                "📅 Теперь введите год для анализа (например, 2025):"
            )
            
            await state.set_state(CalculationStates.waiting_for_year)
        else:
            await message.answer(
                f"❌ Поставщик с кодом/названием '{user_input}' не найден.\n\n"
                "Попробуйте снова или выберите из списка:"
            )
            
            # Показываем список поставщиков снова
            suppliers = DatabaseService.get_available_suppliers(connection)
            if suppliers:
                await state.update_data(suppliers=suppliers)
                
                keyboard = InlineKeyboards.create_suppliers_keyboard(suppliers)
                
                await message.answer(
                    f"🏢 Выберите поставщика для анализа:\n\nНайдено {len(suppliers)} поставщиков\n\n"
                    "Или нажмите '🔢 Ввести код поставщика' если знаете код",
                    reply_markup=keyboard
                )
                
                await state.set_state(CalculationStates.waiting_for_supplier)
    
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    finally:
        connection.close()


async def process_year_input(message: types.Message, state: FSMContext):
    """Обработка ввода года"""
    try:
        year = int(message.text.strip())
        if YEAR_RANGE_MIN <= year <= YEAR_RANGE_MAX:
            await state.update_data(year=year)
            
            # Создаем клавиатуру с месяцами
            keyboard = InlineKeyboards.create_months_keyboard()
            
            await message.answer(
                f"✅ Год: {year}\n\n📅 Выберите месяц:",
                reply_markup=keyboard
            )
            
            await state.set_state(CalculationStates.waiting_for_month)
        else:
            await message.answer(f"❌ Год должен быть между {YEAR_RANGE_MIN} и {YEAR_RANGE_MAX}. Попробуйте снова:")
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный год (например, 2025):")


async def handle_unknown_message(message: types.Message, state: FSMContext):
    """Обработка неизвестных сообщений и команд"""
    
    # Проверяем, является ли сообщение командой
    is_command = message.text and message.text.startswith('/')
    
    if is_command:
        help_text = f"""
❌ <b>Неизвестная команда: {message.text}</b>

<b>Доступные команды:</b>
/start - Начать работу с ботом
/help - Показать справку

<b>Доступные действия:</b>
📊 Начать расчет - Запустить расчет часов поставщика
📊 Новый расчет - Выполнить новый расчет

Используйте /help для получения подробной справки.
        """
    else:
        help_text = """
🤖 <b>Неизвестное сообщение</b>

<b>Доступные команды:</b>
/start - Начать работу с ботом
/help - Показать справку

<b>Доступные действия:</b>
📊 Начать расчет - Запустить расчет часов поставщика
📊 Новый расчет - Выполнить новый расчет

<b>Как использовать бота:</b>
1. Нажмите "📊 Начать расчет"
2. Выберите поставщика из списка ИЛИ введите его код/название
3. Введите год (2020-2030)
4. Выберите месяц
5. Получите результат расчета

<b>Поиск поставщика:</b>
• Выберите из списка по кнопке
• Или введите код (например, 1064)
• Или введите название компании

Если вы находитесь в процессе расчета, следуйте инструкциям бота.
        """
    
    await message.answer(help_text, parse_mode="HTML")