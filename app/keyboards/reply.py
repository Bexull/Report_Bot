from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class ReplyKeyboards:
    """Класс для создания reply клавиатур"""
    
    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        """Главное меню"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📊 Начать расчет")]],
            resize_keyboard=True
        )
        return keyboard

    @staticmethod
    def get_new_calculation_menu() -> ReplyKeyboardMarkup:
        """Меню для нового расчета"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📊 Новый расчет")]],
            resize_keyboard=True
        )
        return keyboard