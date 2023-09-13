from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from attrs import define, field
from config import *


storage = RedisStorage2()
storage2 = RedisStorage2()
# storage = MemoryStorage()
scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
scheduler.start()

bot_client = Bot(token=str(token_client), parse_mode=types.ParseMode.HTML)
bot_driver = Bot(token=str(token_driver), parse_mode=types.ParseMode.HTML)

dp_client = Dispatcher(bot_client, storage=storage)
dp_driver = Dispatcher(bot_driver, storage=storage2)



