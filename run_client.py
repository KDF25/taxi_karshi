from aiogram.utils import executor

from dispatcher import dp_client
from handlers.client.active_order import ActiveOrderClient
from handlers.client.cashback import CashbackClient
from handlers.client.change_phone import ChangePhoneClient
from handlers.client.menu import MenuClient
from handlers.client.tariffs import TariffsClient
from handlers.client.taxi import TaxiClient
from handlers.client.delivery import DeliveryClient
from aiohttp import web

from handlers.client.truck import TruckClient
from looping import pg


async def on_startup(dp):
	await pg.sql_start()
	print("бот вышел в онлайн")

app = web.Application()


menu_client = MenuClient()
taxi_client = TaxiClient()
delivery_client = DeliveryClient()
truck_client = TruckClient()
active_order = ActiveOrderClient()
tariffs = TariffsClient()
change_phone = ChangePhoneClient()
cashback = CashbackClient()

menu_client.register_handlers(dp=dp_client)
taxi_client.register_handlers(dp=dp_client)
delivery_client.register_handlers(dp=dp_client)
truck_client.register_handlers(dp=dp_client)
active_order.register_handlers(dp=dp_client)
tariffs.register_handlers(dp=dp_client)
change_phone.register_handlers(dp=dp_client)
cashback.register_handlers(dp=dp_client)


executor.start_polling(dispatcher=dp_client, skip_updates=True, on_startup=on_startup)