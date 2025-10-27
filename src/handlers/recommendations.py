from telegram import Update
from telegram.ext import ContextTypes
from src.openai_client import simple_prompt

async def recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else "зроби ідеї вихідних для сім'ї з дітьми в Києві"
    text = await simple_prompt("Тревел-рекомендації:", query)
    await update.message.reply_text(text)
