from aiogram import types
from aiogram.filters import Command

from app.keyboards.reply import ReplyKeyboards
from app.config.settings import HOURS_PER_FTE, COST_PER_FTE, YEAR_RANGE_MIN, YEAR_RANGE_MAX


async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = """
🚀 Добро пожаловать в бот расчета часов поставщиков!

Этот бот поможет вам рассчитать:
• Фактически отработанные часы
• Планируемые часы по FTE
• Анализ недоработки/переработки
• Стоимость неотработанных часов

Для начала работы нажмите кнопку ниже 👇
    """
    
    keyboard = ReplyKeyboards.get_main_menu()
    await message.answer(welcome_text, reply_markup=keyboard)


async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
📚 <b>Справка по использованию бота</b>

<b>Команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку

<b>Как использовать:</b>
1. Нажмите "📊 Начать расчет"
2. Выберите поставщика из списка ИЛИ введите его код/название
3. Введите год ({YEAR_RANGE_MIN}-{YEAR_RANGE_MAX})
4. Выберите месяц
5. Получите результат расчета

<b>Поиск поставщика:</b>
• Выберите из списка по кнопке
• Или введите код (например, 1064)
• Или введите название компании

<b>Что рассчитывает бот:</b>
• Фактически отработанные часы
• Планируемые часы по FTE
• Анализ недоработки/переработки
• Стоимость неотработанных часов

<b>Константы:</b>
• {HOURS_PER_FTE} часов на 1 FTE
• {COST_PER_FTE:,} тенге на 1 FTE
    """
    
    await message.answer(help_text, parse_mode="HTML")


async def cmd_unknown(message: types.Message):
    """Обработчик неизвестных команд"""
    unknown_text = f"""
❌ <b>Неизвестная команда: {message.text}</b>

<b>Доступные команды:</b>
/start - Начать работу с ботом
/help - Показать справку

<b>Доступные действия:</b>
📊 Начать расчет - Запустить расчет часов поставщика
📊 Новый расчет - Выполнить новый расчет

Используйте /help для получения подробной справки.
    """
    
    await message.answer(unknown_text, parse_mode="HTML")