import json
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.utils.exceptions import MessageNotModified

from dispatcher import bot_client as bot, bot_driver
from keyboards.inline.client.inline import InlineClient
from keyboards.reply.driver import ReplyDriver
from looping import pg
from text.client.formDelivery import FormDelivery
from text.client.formPassenger import FormPassenger
from text.client.formTruck import FormTruck
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class ActiveOrderClient(StatesGroup):
    async def menu_active_order(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            orders = await pg.select_active_order(client_id=message.from_user.id, language='rus')
            await self._order(orders, data, message)

    @staticmethod
    async def _order(orders: list, data: dict, message: types.Message):
        if len(orders) == 0:
            Lang: Model = Txt.language[data.get('lang')]
            await bot.send_message(chat_id=message.from_user.id, text=Lang.active_order.noOrder)
            return

        for order_client_id, order_accept_id,order_type,  location, comment, phone_client, color, model, number, phone_driver, name, DT, car_type in orders:
            data['order_client_id'], data['order_accept_id'], data['type'], data['location'], \
                data['comment'], data['client_phone'], data['color'], data['model'], \
                data['number'], data['driver_phone'], data['name'] = order_client_id, order_accept_id, order_type,\
                json.loads(location), comment, phone_client, color, model, number, phone_driver, name

            if car_type == "delivery":
                form = FormDelivery(data=data)
            elif car_type == "taxi":
                form = FormPassenger(data=data)
            elif car_type == "truck":
                form = FormTruck(data=data)
            else:
                continue

            if data['order_accept_id'] is None:
                text = await form.menu_active_order()
            else:
                text = await form.menu_active_order_accepted()

            inline = InlineClient(order_id=order_client_id, language=data.get('lang'))
            if DT is None:
                await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await inline.menu_active_order())
            else:
                await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await inline.menu_location())

    @staticmethod
    async def menu_location(call: types.CallbackQuery):
        await call.answer()
        location = await pg.active_location(order_client_id=int(call.data.split('_')[1]))
        await bot.send_location(chat_id=call.from_user.id, latitude=location['latitude'], longitude=location['longitude'])

    @staticmethod
    async def menu_cancel(call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            inline = InlineClient(order_id=int(call.data.split('_')[1]), language=data.get('lang'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=Lang.active_order.cancel, reply_markup=await inline.menu_delete_active_order())
            await call.answer()

    async def menu_delete(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            with suppress(MessageNotModified):
                await call.answer()
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=Lang.active_order.delete)
            await pg.update_order(order_client_id=int(call.data.split('_')[1]), status=False)
            data["order_driver_id"] = await pg.update_cancel_order(order_client_id=int(call.data.split('_')[1]))
            if data["order_driver_id"] is not None:
                await self._delete_driver(data)

    @staticmethod
    async def _delete_driver(data: dict):
        driver_id, lang = await pg.select_route_driver2(order_driver_id=data["order_driver_id"][0])
        await pg.update_on_route_status(driver_id=driver_id, status=False)
        await pg.update_driver_wallet_payment(driver_id=driver_id, cash=Txt.money.driver.order_min_price)
        Lang: Model = Txt.language[lang]
        reply = ReplyDriver(language=data.get('lang'))
        await bot_driver.send_message(chat_id=driver_id, text=Lang.active_order.delete_driver, reply_markup=await reply.start_online())

    def register_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.menu_active_order, text=Txt.client.menu.order,                                 state='*')
        dp.register_callback_query_handler(self.menu_location, lambda x: x.data.startswith("location"),                 state="*")
        dp.register_callback_query_handler(self.menu_cancel, lambda x: x.data.startswith("cancel"),                     state="*")
        dp.register_callback_query_handler(self.menu_delete, lambda x: x.data.startswith("delete"),                     state="*")



