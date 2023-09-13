import json

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup

from dispatcher import bot_driver as bot
from keyboards.inline.driver.inline import InlineDriverData
from looping import pg
from text.driver.formNewOrder import FormNewOrder
from text.function.function import TextFunc
from text.language.main import Text_main

Txt = Text_main()
func = TextFunc()


class OrderDataDriver(StatesGroup):
    async def menu_order_data(self, message:  types.Message, state: FSMContext):
        async with state.proxy() as data:
            await func.personal_data(message, data)
            await self.get_accept_order(message, data)
            form = FormNewOrder(language=data.get('lang'), data=data)
            inline = InlineDriverData(order_id=data['order_client_id'], language=data.get('lang'))
            await bot.send_message(chat_id=message.from_user.id, text=await form.menu_accept_taxi(), reply_markup=await inline.menu_cancel_active_order())
            await bot.send_location(chat_id=message.from_user.id, latitude=data['location']['latitude'], longitude=data['location']['longitude'])

    @staticmethod
    async def get_accept_order(message:  types.Message, data: dict):
        data['client_id'], data['lang_client'], data['location'], data['type'],  data['order_accept_id'], \
            data['order_client_id'], data['phone_client'], data['lang_client'], data['comment'], data['cashback'] = \
            await pg.select_active_order_driver(driver_id=message.from_user.id)
        data['location'] = json.loads(data['location'])
        data['spot'] = await pg.select_spot(location=data['location'])
        data['color'] = await pg.id_to_color(id=data['color_id'], language=data['lang_client'])

    def register_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.menu_order_data, text=Txt.driver.menu.orderData,                               state='*')




