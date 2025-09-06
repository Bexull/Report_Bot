from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from app.config.settings import MONTH_NAMES_TITLE


class InlineKeyboards:
    """Класс для создания inline клавиатур"""
    
    @staticmethod
    def create_suppliers_keyboard(suppliers: List[str]) -> InlineKeyboardMarkup:
        """Создание клавиатуры с поставщиками"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for i, supplier in enumerate(suppliers):
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"{i+1}. {supplier}",
                    callback_data=f"supplier_{i}"
                )
            ])
        
        # Добавляем кнопку для ввода кода поставщика
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="🔢 Ввести код поставщика",
                callback_data="supplier_code_input"
            )
        ])
        
        return keyboard

    @staticmethod
    def create_months_keyboard() -> InlineKeyboardMarkup:
        """Создание клавиатуры с месяцами"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for i, month_name in enumerate(MONTH_NAMES_TITLE):
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"{i+1}. {month_name}",
                    callback_data=f"month_{i+1}"
                )
            ])
        
        return keyboard