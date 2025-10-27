from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.openai_client import achat

FACT_PROMPT = (
    "Згенеруй один цікавий, неочевидний факт українською (60–100 слів). "
    "Стиль — дружній, без номерів і списків, лише абзац. Теми: історія, наука, культура або природа."
)

def random_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Хочу ще факт", callback_data="random_more")],
        [InlineKeyboardButton("Закінчити", callback_data="end_start")],
    ])

async def send_random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Надсилаємо заготовлене зображення
    try:
        with open("assets/random.jpg", "rb") as img:
            await update.message.reply_photo(photo=img, caption="Випадковий факт 🔎")
    except Exception:
        await update.message.reply_text("Випадковий факт 🔎")

    # Запит до ChatGPT із фіксованим промптом
    text = await achat([
        {"role": "system", "content": "Ти доброзичливий помічник."},
        {"role": "user", "content": FACT_PROMPT},
    ])
    await update.message.reply_text(text, reply_markup=random_keyboard())

async def handle_random_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "random_more":
        # повторюємо /random
        fake_update = Update(update.update_id, message=query.message)  # невеликий трюк
        fake_update.message = query.message
        # використовуємо caption/message.from_user для узгодженості
        await query.message.reply_text("Ще один факт завантажую…")
        await send_random_fact(fake_update, context)
    elif query.data == "end_start":
        await query.message.reply_text("Повертаюся в початок. Напиши /start, щоб знову почати.")
