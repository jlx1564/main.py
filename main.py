import requests
import logging
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Telegram API Token
API_TOKEN = "7980626247:AAEtckoqoNQEUEVp7GT9I6SRMA-SN86TcF0"
CHANNEL_ID = "@piterfr"

# URL для парсинга
TIMEPAD_URL = "https://afisha.timepad.ru/saint-petersburg/search?price=free"

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dp["bot"] = bot

scheduler = AsyncIOScheduler()

# Логирование
logging.basicConfig(level=logging.INFO)

async def fetch_events():
    """Функция парсинга бесплатных событий с Timepad."""
    response = requests.get(TIMEPAD_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    events = []

    for event in soup.select("article.eventpage"):  # Основной контейнер события
        title = event.select_one("h1.typography.typography__subheader").text.strip()
        date_time = event.select_one("div.typography.typography--responsive.typography--no-padding.typography__caption.cheaderblock--caption.tcaptionmargin").text.strip()
        location = event.select_one("div.typography.typography--responsive.typography--no-padding.typography__small.tsmallmargin.t-color-gray-50").text.strip()
        link = event.find("a", href=True)["href"]

        event_text = (f"📅 Дата и время: {date_time}\n"
                      f"📍 Место: {location}\n"
                      f"📝 {title}\n"
                      f"🔗 [Регистрация]({link})")
        events.append(event_text)
    return events

async def post_events():
    """Функция для отправки событий в Telegram-канал."""
    events = await fetch_events()
    for event in events:
        try:
            await bot.send_message(CHANNEL_ID, event, parse_mode="Markdown")
            await asyncio.sleep(2)  # Задержка между отправками
        except Exception as e:
            logging.error(f"Ошибка при отправке: {e}")

async def main():
    """Основная функция запуска бота и расписания обновлений."""
    scheduler.add_job(post_events, 'interval', hours=1)  # Обновлять каждый час
    scheduler.start()
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
