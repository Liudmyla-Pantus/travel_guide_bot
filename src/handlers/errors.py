import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled exception while handling update: %s", update)
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "Ой, сталась помилка. Я вже записав лог і спробую відновитись 🙏"
            )
    except Exception:  # noqa: BLE001
        pass
