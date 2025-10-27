from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.openai_client import achat

PERSONAS = {
    "einstein": "Відповідай як Альберт Ейнштейн: доброзичливо, з науковими аналогіями, просто про складне.",
    "mask": "Відповідай як Ілон Маск: візіонерсько, коротко, з акцентом на технології й майбутнє.",
    "shevchenko": "Відповідай як Тарас Шевченко: по-українськи, піднесено й образно, але зрозуміло сучасному читачу.",
}

def talk_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Ейнштейн", callback_data="talk_einstein"),
         InlineKeyboardButton("Маск", callback_data="talk_mask")],
        [InlineKeyboardButton("Шевченко", callback_data="talk_shevchenko")],
    ])

def end_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Закінчити", callback_data="end_start")]
    ])

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open("assets/talk.jpg", "rb") as img:
            await update.message.reply_photo(photo=img, caption="Обери співрозмовника:", reply_markup=talk_keyboard())
    except Exception:
        await update.message.reply_text("Обери співрозмовника:", reply_markup=talk_keyboard())
    context.chat_data["mode"] = "talk"
    context.chat_data["persona"] = None

async def handle_talk_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if q.data.startswith("talk_"):
        key = q.data.split("_", 1)[1]
        if key in PERSONAS:
            context.chat_data["persona"] = PERSONAS[key]
            await q.message.reply_text("Обрано. Пиши повідомлення — я відповідатиму в стилі обраної особистості.", reply_markup=end_keyboard())
    elif q.data == "end_start":
        await q.message.reply_text("Повертаюся в початок. Напиши /start, щоб знову почати.")
        context.chat_data["mode"] = None
        context.chat_data["persona"] = None

async def talk_on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if context.chat_data.get("mode") != "talk" or not context.chat_data.get("persona"):
        return False
    system = context.chat_data["persona"]
    user = update.message.text.strip()
    reply = await achat([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])
    await update.message.reply_text(reply, reply_markup=end_keyboard())
    return True
