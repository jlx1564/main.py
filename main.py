import requests
import logging
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Telegram API Token
API_TOKEN = "7980626247:AAEtckoqoNQEUEVp7GT9I6SRMA-SN86TcF0"
CHANNEL_ID = "@piterfr"

# URL для парсинга
TIMEPAD_URL = "https://afisha.timepad.ru/saint-petersburg/search?price=free"

# Инициализация бота
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(storage=MemoryStorage())  # ✅ Aiogram 3.x создаём без bot
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

        if title_tag and date_time_tag and location_tag
