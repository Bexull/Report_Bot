import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import register_handlers

# Загружаем переменные окружения
load_dotenv()

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE"))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def main():
    """Главная функция"""
    print("🚀 Запуск бота расчета часов поставщиков...")
    
    # Регистрируем обработчики
    register_handlers(dp)
    
    # Удаляем webhook и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("✅ Бот успешно запущен!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот выключен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
