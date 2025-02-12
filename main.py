import requests
import logging
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Telegram API Token
API_TOKEN = "7980626247:AAEtckoqoNQEUEVp7GT9I6SRMA-SN86TcF0"
CHANNEL_ID = "@piterfr"

# URL для парсинга
TIMEPAD_URL = "https://afisha.timepad.ru/saint-petersburg/search?price=free"

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # Теперь без аргумента "bot"
scheduler = AsyncIOScheduler()

# Логирование
logging.basicConfig(level=logging.INFO)

async def fetch_events():
    """Функция парсинга бесплатных событий с Timepad."""
    response = requests.get(TIMEPAD_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    events = []

    for event in soup.select("article.eventpage"):  # Основной контейнер события
        title_tag = event.select_one("h1.typography.typography__subheader")
        date_time_tag = event.select_one("div.typography.typography--responsive.typography--no-padding.typography__caption.cheaderblock--caption.tcaptionmargin")
        location_tag = event.select_one("div.typography.typography--responsive.typography--no-padding.typography__small.tsmallmargin.t-color-gray-50")
        link_tag = event.find("a", href=True)

        if title_tag and date_time_tag and location_tag and link_tag:
            title = title_tag.text.strip()
            date_time = date_time_tag.text.strip()
            location = location_tag.text.strip()
            link = link_tag["href"]

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
    scheduler.add_job(post_events, "interval", hours=1)  # Обновлять каждый час
    scheduler.start()

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)  # Удаление старых обновлений
    await dp.start_polling(bot)  # Aiogram 3.x требует передавать bot в start_polling

if __name__ == "__main__":
    asyncio.run(main())
