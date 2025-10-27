from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.openai_client import achat

LANGS = {"EN": "англійську", "PL": "польську", "DE": "німецьку", "UA": "українську"}

def translate_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("EN", callback_data="tr_lang_EN"),
         InlineKeyboardButton("PL", callback_data="tr_lang_PL"),
         InlineKeyboardButton("DE", callback_data="tr_lang_DE"),
         InlineKeyboardButton("UA", callback_data="tr_lang_UA")],
        [InlineKeyboardButton("Змінити мову", callback_data="tr_change"),
         InlineKeyboardButton("Закінчити", callback_data="end_start")]
    ])

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Оберіть мову перекладу:", reply_markup=translate_keyboard())
    context.chat_data["mode"] = "translate"
    context.chat_data["tr_lang"] = None

async def handle_translate_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    data = q.data
    if data.startswith("tr_lang_"):
        code = data.split("_")[-1]
        context.chat_data["tr_lang"] = code
        await q.message.reply_text(f"Мову обрано: {code}. Надішліть текст для перекладу.", reply_markup=translate_keyboard())
    elif data == "tr_change":
        context.chat_data["tr_lang"] = None
        await q.message.reply_text("Оберіть нову мову:", reply_markup=translate_keyboard())
    elif data == "end_start":
        await q.message.reply_text("Завершено. Напишіть /start, щоб почати спочатку.")
        context.chat_data["mode"] = None

async def translate_on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if context.chat_data.get("mode") != "translate" or not context.chat_data.get("tr_lang"):
        return False
    code = context.chat_data["tr_lang"]
    lang = LANGS.get(code, "українську")
    text = update.message.text.strip()
    out = await achat([
        {"role": "system", "content": "Ти перекладач. Перекладай максимально природно і точно."},
        {"role": "user", "content": f"Переклади на {lang}: {text}"},
    ], temperature=0.2, max_tokens=400)
    await update.message.reply_text(out, reply_markup=translate_keyboard())
    return True
