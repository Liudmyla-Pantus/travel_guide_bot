from telegram import Update
from telegram.ext import ContextTypes
from src.openai_client import simple_prompt

async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) if context.args else "Львів"
    text = await simple_prompt("Лайфхаки подорожей:", f"Дай 7 практичних порад для міста {city}.")
    await update.message.reply_text(text)
