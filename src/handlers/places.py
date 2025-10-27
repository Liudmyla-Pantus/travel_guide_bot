from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, filters,
)
from src.openai_client import generate_place_guide

ASK_PLACE, ASK_STYLE, ASK_BUDGET = range(3)

async def start_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Куди їхати/яке місце описати? (місто/країна/локація)")
    return ASK_PLACE

async def ask_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["place"] = update.message.text.strip()
    await update.message.reply_text(
        "Який стиль подорожі? (сімейний, бюджетний, гастро, романтичний) або «пропустити»"
    )
    return ASK_STYLE

async def ask_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txt = update.message.text.strip()
    context.user_data["style"] = None if txt.lower() == "пропустити" else txt
    await update.message.reply_text("Орієнтовний бюджет? (низький/середній/високий) або «пропустити»")
    return ASK_BUDGET

async def build_and_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txt = update.message.text.strip()
    context.user_data["budget"] = None if txt.lower() == "пропустити" else txt

    place = context.user_data.get("place")
    style = context.user_data.get("style")
    budget = context.user_data.get("budget")

    await update.message.reply_text("Готую рекомендації…")
    guide = await generate_place_guide(place, style, budget)
    await update.message.reply_text(guide)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

def build_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("place", start_flow)],
        states={
            ASK_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_style)],
            ASK_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_budget)],
            ASK_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, build_and_reply)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="place_conv",
    )
