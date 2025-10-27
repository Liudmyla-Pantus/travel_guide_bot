from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.openai_client import achat

TOPICS = ["Історія", "Географія", "Наука", "Культура"]

def topics_keyboard() -> InlineKeyboardMarkup:
    row1 = [InlineKeyboardButton(t, callback_data=f"quiz_topic_{i}") for i, t in enumerate(TOPICS[:2])]
    row2 = [InlineKeyboardButton(t, callback_data=f"quiz_topic_{i}") for i, t in enumerate(TOPICS[2:], start=2)]
    return InlineKeyboardMarkup([row1, row2])

def quiz_ctrl_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Ще питання", callback_data="quiz_more"),
         InlineKeyboardButton("Змінити тему", callback_data="quiz_change")],
        [InlineKeyboardButton("Закінчити", callback_data="end_start")]
    ])

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open("assets/quiz.jpg", "rb") as img:
            await update.message.reply_photo(photo=img, caption="Обери тему квізу:", reply_markup=topics_keyboard())
    except Exception:
        await update.message.reply_text("Обери тему квізу:", reply_markup=topics_keyboard())
    context.chat_data.update({"mode": "quiz", "quiz_topic": None, "quiz_q": None, "score": 0, "total": 0})

async def _get_question(topic: str) -> str:
    return await achat([
        {"role": "system", "content": "Ти генератор квізів. Поверни одне запитання українською, без відповіді, одне речення."},
        {"role": "user", "content": f"Тема: {topic}. Згенеруй цікаве, але коротке запитання для школяра."},
    ], temperature=0.7, max_tokens=120)

async def _check_answer(topic: str, question: str, answer: str) -> tuple[bool, str]:
    text = await achat([
        {"role": "system", "content": "Ти перевіряєш відповіді на квіз. Поверни JSON: {\"correct\": true/false, \"explain\": \"...\"}."},
        {"role": "user", "content": f"Тема: {topic}\nПитання: {question}\nВідповідь користувача: {answer}\nОціни об'єктивно."},
    ], temperature=0.0, max_tokens=180)
    # Дуже грубо: якщо немає валідного JSON — спробуємо евристично
    import json
    try:
        data = json.loads(text)
        return bool(data.get("correct")), str(data.get("explain", ""))
    except Exception:
        ok = any(w in text.lower() for w in ["правиль", "вірн", "так"])
        return ok, text

async def handle_quiz_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    data = q.data

    if data.startswith("quiz_topic_"):
        idx = int(data.split("_")[-1])
        topic = TOPICS[idx]
        context.chat_data["quiz_topic"] = topic
        context.chat_data["score"] = 0
        context.chat_data["total"] = 0
        # перше питання
        question = await _get_question(topic)
        context.chat_data["quiz_q"] = question
        await q.message.reply_text(f"Тема: {topic}\nПерше питання:\n\n{question}")
        await q.message.reply_text("Ваша відповідь?", reply_markup=quiz_ctrl_keyboard())

    elif data == "quiz_more":
        topic = context.chat_data.get("quiz_topic")
        if not topic:
            await q.message.reply_text("Спочатку оберіть тему.", reply_markup=topics_keyboard())
            return
        question = await _get_question(topic)
        context.chat_data["quiz_q"] = question
        await q.message.reply_text(f"Нове питання:\n\n{question}")
        await q.message.reply_text("Ваша відповідь?", reply_markup=quiz_ctrl_keyboard())

    elif data == "quiz_change":
        context.chat_data["quiz_topic"] = None
        context.chat_data["quiz_q"] = None
        await q.message.reply_text("Оберіть нову тему:", reply_markup=topics_keyboard())

    elif data == "end_start":
        await q.message.reply_text("Квіз завершено. Напишіть /start, щоб почати спочатку.")
        context.chat_data["mode"] = None

async def quiz_on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if context.chat_data.get("mode") != "quiz":
        return False
    topic = context.chat_data.get("quiz_topic")
    question = context.chat_data.get("quiz_q")
    if not topic or not question:
        return False
    answer = update.message.text.strip()
    ok, explain = await _check_answer(topic, question, answer)
    context.chat_data["total"] = context.chat_data.get("total", 0) + 1
    if ok:
        context.chat_data["score"] = context.chat_data.get("score", 0) + 1
    score = context.chat_data["score"]; total = context.chat_data["total"]
    verdict = "✅ Правильно!" if ok else "❌ Неправильно."
    await update.message.reply_text(f"{verdict}\n\nПояснення: {explain}\n\nРахунок: {score}/{total}", reply_markup=quiz_ctrl_keyboard())
    # після відповіді чекаємо натискання кнопок або ще відповідь — але краще керуватись кнопками
    return True
