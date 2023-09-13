from aiogram.utils import executor
from aiohttp import web

from dispatcher import dp_driver
from handlers.driver.active_order import ActiveOrderDriver
from handlers.driver.menu import MenuDriver
from handlers.driver.on_route import OnRouteDriver
from handlers.driver.order_data import OrderDataDriver
from handlers.driver.registration_taxi import RegistrationDriverCar
from handlers.driver.personal_data import PersonalCabinet
from handlers.driver.online import OnlineDriver
from handlers.driver.new_order import NewOrderDriver
from handlers.driver.registration_truck import RegistrationDriverTruck
from handlers.driver.wallet import WalletDriver
from handlers.group.menu import MenuGroup
from looping import pg


async def on_startup(dp):
	await pg.sql_start()
	print("бот вышел в онлайн")

app = web.Application()

menu_driver = MenuDriver()
registration_driver_car = RegistrationDriverCar()
registration_driver_truck = RegistrationDriverTruck()
personal_data = PersonalCabinet()
online = OnlineDriver()
group = MenuGroup()
new_order = NewOrderDriver()
active_order = ActiveOrderDriver()
order_data = OrderDataDriver()
on_route = OnRouteDriver()
wallet = WalletDriver()

menu_driver.register_handlers(dp=dp_driver)
registration_driver_car.register_handlers(dp=dp_driver)
registration_driver_truck.register_handlers(dp=dp_driver)
personal_data.register_handlers(dp=dp_driver)
online.register_handlers(dp=dp_driver)
group.register_handlers(dp=dp_driver)
new_order.register_handlers(dp=dp_driver)
active_order.register_handlers(dp=dp_driver)
order_data.register_handlers(dp=dp_driver)
on_route.register_handlers(dp=dp_driver)
wallet.register_handlers(dp=dp_driver)

executor.start_polling(dispatcher=dp_driver, skip_updates=True, on_startup=on_startup)

