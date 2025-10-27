# 🌍 Travel Guide Bot  
**Telegram-бот**, що створює короткі тревел-гайди та демонструє роботу з OpenAI API.  
Проєкт виконано в рамках навчання **JavaRush Python University**.

---

## ✨ Основний функціонал

- 🧳 Генерує тревел-гайд (маршрут, цікаві місця, поради) за введеною країною або містом.  
- 💬 Спілкується у форматі діалогу з користувачем.  
- 🧠 Використовує OpenAI API для створення текстів.  
- 📸 Має окремі розділи з інтерактивними кнопками:
  - **Random facts** — випадкові факти про подорожі.  
  - **Quiz** — коротка вікторина.  
  - **Talk** — вільна розмова з ботом.  
  - **GPT** — відповіді на будь-які запитання.

---

## ⚙️ Технології

- **Python 3.13**  
- **python-telegram-bot v21+**  
- **OpenAI API (chat completions)**  
- **asyncio / aiohttp**  
- **Git + GitHub**

---

## 🚀 Як запустити локально

1. Клонувати репозиторій:
   ```bash
   git clone https://github.com/Liudmyla-Pantus/travel_guide_bot.git
   cd travel_guide_bot
2. Створити віртуальне середовище:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
3. Встановити залежності:
   ```bash
   pip install -r requirements.txt
4. Створити файл .env у корені проєкту:
   ```ini
   TELEGRAM_BOT_TOKEN=тут_токен_твоего_бота
   OPENAI_API_KEY=ключ_OpenAI_із_файлу_openai-token.txt
5. Запустити бота:
   ```bash
   python -m src.bot
   