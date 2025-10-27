from telegram import Update
from telegram.ext import ContextTypes
from src.openai_client import achat

async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Надсилаємо заготовлене зображення
    try:
        with open("assets/gpt.jpg", "rb") as img:
            await update.message.reply_photo(photo=img, caption="Режим ChatGPT: надішли повідомлення текстом ⌨️")
    except Exception:
        await update.message.reply_text("Режим ChatGPT: надішли повідомлення текстом ⌨️")

    context.chat_data["mode"] = "gpt"

async def gpt_on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if context.chat_data.get("mode") != "gpt":
        return False
    user_text = update.message.text.strip()
    reply = await achat([
        {"role": "system", "content": "Ти корисний асистент. Відповідай українською стисло і по суті."},
        {"role": "user", "content": user_text},
    ])
    await update.message.reply_text(reply)
    return True
