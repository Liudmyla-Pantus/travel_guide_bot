# src/bot.py
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------------- базові налаштування ----------------------

def read_token_file(path: str = "token.txt") -> str | None:
    """Читає токен з token.txt. Підтримує формат KEY=VALUE і прибирає лапки."""
    try:
        raw = open(path, "r", encoding="utf-8").read().strip()
    except FileNotFoundError:
        return None
    if "=" in raw:               # якщо випадково записали TELEGRAM_BOT_TOKEN=...
        raw = raw.split("=", 1)[1].strip()
    return raw.strip('"').strip("'")

load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=os.getenv("LOG_LEVEL", "INFO"),
)
logger = logging.getLogger(__name__)

BOT_TOKEN = read_token_file() or os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Не знайдено токен: token.txt або TELEGRAM_BOT_TOKEN у .env")

# ---------------------- імпорти хендлерів ------------------------

# 0) Помилки (якщо є)
try:
    from src.handlers.errors import error_handler
except Exception:  # не обов’язково
    error_handler = None

# Travel /place (залишаємо твою основну фічу, якщо модуль існує)
HAS_PLACES = False
try:
    from src.handlers.places import build_handler as build_places
    HAS_PLACES = True
except Exception:
    HAS_PLACES = False

from src.handlers.random_fact import send_random_fact, handle_random_callbacks
from src.handlers.gpt import gpt_command, gpt_on_text
from src.handlers.talk import talk_command, handle_talk_callbacks, talk_on_text
from src.handlers.quiz import quiz_command, handle_quiz_callbacks, quiz_on_text
from src.handlers.translator import (
    translate_command,
    handle_translate_callbacks,
    translate_on_text,
)


# ---------------------- команди ------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🌍 Привіт! Я тревел-бот ✈️\n\n"
        "Основне:\n"
        "/place — згенерувати тревел-ґайд (твоя головна функція)\n\n"
        "Навчальні модулі (для завдання JR):\n"
        "/random — випадковий факт (картинка + кнопки)\n"
        "/gpt — постав запитання ChatGPT\n"
        "/talk — діалог зі «знаменитістю»\n"
        "/quiz — міні-квіз з рахунком\n"
        "/translate — перекладач із вибором мови\n"
    )
    await update.message.reply_text(text)

# ---------------------- роутер тексту ------------------------

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Усі НЕкомандні тексти передаємо в активний режим.
    Порядок важливий — хто обробив, той повертає True й інші не викликаються.
    """
    if await gpt_on_text(update, context):
        return
    if await talk_on_text(update, context):
        return
    if await quiz_on_text(update, context):
        return
    if await translate_on_text(update, context):
        return
    await update.message.reply_text("Напишіть /start, щоб побачити меню.")

# ---------------------- запуск додатку ------------------------

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Помилки
    if error_handler:
        app.add_error_handler(error_handler)

    # /start
    app.add_handler(CommandHandler("start", start))

    # Твоє /place (якщо модуль існує і містить build_handler())
    if HAS_PLACES:
        app.add_handler(build_places())

    # 1) /random + його кнопки (random_more, end_start)
    app.add_handler(CommandHandler("random", send_random_fact))
    app.add_handler(CallbackQueryHandler(handle_random_callbacks, pattern=r"^(random_more|end_start)$"))

    # 2) /gpt (режим чату з GPT)
    app.add_handler(CommandHandler("gpt", gpt_command))

    # 3) /talk + кнопки (talk_..., end_start)
    app.add_handler(CommandHandler("talk", talk_command))
    app.add_handler(CallbackQueryHandler(handle_talk_callbacks, pattern=r"^(talk_.*|end_start)$"))

    # 4) /quiz + кнопки (quiz_..., end_start)
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CallbackQueryHandler(handle_quiz_callbacks, pattern=r"^(quiz_.*|end_start)$"))

    # 5) /translate + кнопки (tr_..., end_start)
    app.add_handler(CommandHandler("translate", translate_command))
    app.add_handler(CallbackQueryHandler(handle_translate_callbacks, pattern=r"^(tr_.*|end_start)$"))

    # Роутер простих текстів (обов’язково після команд і callback'ів!)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    logger.info("🚀 Бот запущено!")
    app.run_polling()

if __name__ == "__main__":
    main()
