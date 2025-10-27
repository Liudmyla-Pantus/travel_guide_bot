import os
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Завантажуємо .env, якщо він є
load_dotenv()

# Читаємо OpenAI ключ — спершу з .env, потім із openai-token.txt
_api_key = os.getenv("OPENAI_API_KEY")

if not _api_key and os.path.exists("openai-token.txt"):
    with open("openai-token.txt", "r", encoding="utf-8") as f:
        _api_key = f.read().strip()

if not _api_key:
    raise RuntimeError("❌ Не знайдено OpenAI API ключ! Перевір .env або openai-token.txt")

# Ініціалізуємо клієнт
client = AsyncOpenAI(api_key=_api_key)
logger = logging.getLogger(__name__)


# ---- Основна функція для асинхронного запиту ----
async def achat(messages: list[dict], temperature: float = 0.7, max_tokens: int = 500) -> str:
    """
    Виконує асинхронний запит до ChatGPT.
    :param messages: список повідомлень [{'role': 'system'/'user', 'content': '...'}]
    :param temperature: креативність відповіді
    :param max_tokens: обмеження на кількість токенів у відповіді
    :return: відповідь ChatGPT (str)
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"❌ Помилка під час виклику OpenAI API: {e}")
        return "Вибач, не вдалося отримати відповідь від ChatGPT 😔"


# ---- Функція, на яку посилаються хендлери (наприклад, places.py) ----
async def generate_place_guide(place: str, style: str | None = None, budget: str | None = None) -> str:
    """
    Генерує короткий тревел-гайд. Сумісна зі старим імпортом:
    from src.openai_client import generate_place_guide
    """
    user = f"Місце: {place}."
    if style:
        user += f" Стиль: {style}."
    if budget:
        user += f" Бюджет: {budget}."
    messages = [
        {"role": "system", "content": "Ти тревел-експерт. Відповідай українською, стисло і практично."},
        {"role": "user",  "content": f"Зроби короткий тревел-гайд (маршрут 1-2 дні, ТОП місця, поради). {user}"},
    ]
    return await achat(messages, temperature=0.6, max_tokens=700)
