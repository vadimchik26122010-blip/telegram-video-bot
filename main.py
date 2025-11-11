import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = os.environ.get('TELEGRAM_TOKEN')

def main():
    logger.info("=== Бот запускается ===")
    
    # Проверяем токен
    if not TOKEN:
        logger.error("❌ ТОКЕН НЕ НАЙДЕН! Проверьте переменную TELEGRAM_TOKEN в Render")
        return
    
    logger.info(f"✅ Токен получен (первые 10 символов): {TOKEN[:10]}...")
    
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        logger.info("✅ Библиотеки импортированы успешно")
        
        # Создаем приложение
        application = Application.builder().token(TOKEN).build()
        logger.info("✅ Приложение создано")
        
        # Простой обработчик для теста
        async def start(update, context):
            await update.message.reply_text("✅ Бот работает! Тест успешен!")
        
        application.add_handler(CommandHandler("start", start))
        logger.info("✅ Обработчики добавлены")
        
        # Запускаем бота
        logger.info("✅ Бот запускается...")
        application.run_polling()
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        logger.error(f"❌ Общая ошибка: {e}")

if __name__ == '__main__':
    main()
    logger.info("=== Бот завершил работу ===")
