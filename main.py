import os
import tempfile
import subprocess
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = os.environ.get('TELEGRAM_TOKEN')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info("Получено видео")
        
        # Проверяем длительность видео
        if update.message.video.duration > 60:
            await update.message.reply_text("❌ Видео должно быть не длиннее 60 секунд")
            return

        # Скачиваем видео
        file = await update.message.video.get_file()
        logger.info(f"Файл: {file.file_path}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as input_file:
            input_path = input_file.name
            await file.download_to_drive(input_path)
        
        logger.info(f"Видео скачано: {input_path}")
        
        # Создаем временный файл для результата
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as output_file:
            output_path = output_file.name
        
        # Конвертируем в кружочек с помощью FFmpeg
        try:
            logger.info("Начинаем конвертацию FFmpeg")
            
            # Более простая команда FFmpeg
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', 'scale=720:720:force_original_aspect_ratio=increase,crop=720:720',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-an',  # удаляем аудио (для video note не нужно)
                '-y',
                output_path
            ]
            
            logger.info(f"Выполняем команду: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                await update.message.reply_text("❌ Ошибка при обработке видео FFmpeg")
                return
                
            logger.info("FFmpeg завершил успешно")
                
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout")
            await update.message.reply_text("❌ Таймаут при обработке видео")
            return
        except Exception as e:
            logger.error(f"FFmpeg processing error: {e}")
            await update.message.reply_text("❌ Ошибка при конвертации видео")
            return
        
        # Проверяем размер выходного файла
        file_size = os.path.getsize(output_path)
        logger.info(f"Размер выходного файла: {file_size} байт")
        
        if file_size == 0:
            await update.message.reply_text("❌ Получен пустой файл после конвертации")
            return
        
        # Отправляем результат
        logger.info("Отправляем видео-кружочек")
        with open(output_path, 'rb') as video_file:
            await update.message.reply_video_note(video_note=video_file)
        
        logger.info("Видео-кружочек отправлен успешно")
        
        # Удаляем временные файлы
        os.unlink(input_path)
        os.unlink(output_path)
        
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        await update.message.reply_text("❌ Произошла неизвестная ошибка при обработке видео")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для создания видео-кружочков.\n\n"
        "Просто пришли мне видео (до 60 секунд), и я преобразую его в кружочек!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📹 Отправьте мне любое видео (до 60 секунд), и я превращу его в видео-кружочек для Telegram!\n\n"
        "Можно отправить видео из галереи или снять новое."
    )

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
