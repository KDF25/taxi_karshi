import json
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from dispatcher import bot_driver as bot, bot_client
from keyboards.reply.driver import ReplyDriver
from looping import pg
from text.driver.formNewOrder import FormNewOrder
from text.function.function import TextFunc
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()
func = TextFunc()


class NewOrderDriver(StatesGroup):
    async def menu_new_order(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            isAccept, haveMoney = await self._check_order(call, data)
            if isAccept is None and haveMoney is True:
                await self._order_type(call, data)
                await state.set_state("NewOrderDriver:menu_level_new_order")
            elif isAccept is not None:
                Lang: Model = Txt.language[data.get('lang')]
                await call.answer(show_alert=True, text=Lang.alert.driver.order)
            elif haveMoney is False:
                Lang: Model = Txt.language[data.get('lang')]
                await call.answer(show_alert=True, text=Lang.alert.driver.notEnoughMoney)
                
    async def _order_type(self, call: types.CallbackQuery, data: dict):
        _type = call.data.split('_')[0]
        if _type == "orderAcceptTaxi":
            await self._accept_taxi(call, data)
        elif _type == "orderAcceptDelivery":
            await self._accept_delivery(call, data)
        elif _type == "orderAcceptTruck":
            await self._accept_truck(call, data)

    @staticmethod
    async def _check_order(call: types.CallbackQuery, data: dict):
        data['order_id'] = int(call.data.split('_')[1])
        data['driver_id'] = call.from_user.id
        isAccept = await pg.check_order_accept(order_id=data['order_id'])
        wallet = await pg.select_every_wallet(driver_id=data['driver_id'])
        data['wallet'] = [i for i in wallet]
        haveMoney = sum(data['wallet']) >= Txt.money.driver.order_min_price
        return isAccept, haveMoney

    async def _accept_taxi(self, call: types.CallbackQuery, data: dict):
        await call.answer()
        form_driver, form_client, reply = await self._accepted(call, data)
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=await form_driver.menu_accept_taxi(), reply_markup=await reply.menu_on_spot())
        await bot.send_location(chat_id=call.from_user.id, latitude=data['location']['latitude'], longitude=data['location']['longitude'])
        await bot_client.send_message(chat_id=data['client_id'], text=await form_client.menu_accept())

    async def _accept_delivery(self, call: types.CallbackQuery, data: dict):
        await call.answer()
        form_driver, form_client, reply = await self._accepted(call, data)
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=await form_driver.menu_accept_delivery_and_truck(), reply_markup=await reply.menu_on_spot())
        await bot.send_location(chat_id=call.from_user.id, latitude=data['location']['latitude'], longitude=data['location']['longitude'])
        await bot_client.send_message(chat_id=data['client_id'], text=await form_client.menu_accept())

    async def _accept_truck(self, call: types.CallbackQuery, data: dict):
        await call.answer()
        form_driver, form_client, reply = await self._accepted(call, data)
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=await form_driver.menu_accept_delivery_and_truck(), reply_markup=await reply.menu_on_spot())
        await bot.send_location(chat_id=call.from_user.id, latitude=data['location']['latitude'], longitude=data['location']['longitude'])
        await bot_client.send_message(chat_id=data['client_id'], text=await form_client.menu_accept_truck())

    async def _accepted(self,  call: types.CallbackQuery, data: dict):
        await self._update_wallet(data)
        await pg.update_order(order_client_id=data['order_id'], status=True)
        await pg.update_on_route_status(driver_id=call.from_user.id, status=True)
        await pg.accept_order(order_client_id=data['order_id'], driver_id=call.from_user.id)
        data['client_id'], data['lang_client'], data['location'], data['type'],  data['order_accept_id'], \
            data['order_client_id'], data['phone_client'], data['lang_client'], data['comment'], data['cashback'] = \
            await pg.select_active_order_driver(driver_id=call.from_user.id)
        data['location'] = json.loads(data['location'])
        data['spot'] = await pg.select_spot(location=data['location'])
        await func.personal_data(call, data)
        data['color'] = await pg.id_to_color(id=data['color_id'], language=data["lang_client"])
        form_driver = FormNewOrder(language=data.get('lang'), data=data)
        form_client = FormNewOrder(language=data.get('lang_client'), data=data)
        reply = ReplyDriver(language=data.get('lang'))
        return form_driver, form_client, reply

    @staticmethod
    async def _update_wallet(data: dict):
        price = Txt.money.driver.order_min_price
        await func.change_wallet(data, price)
        await pg.update_driver_wallet_accept(driver_id=data.get('driver_id'), wallet=data['wallet'])

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_new_order, lambda x: x.data.startswith("orderAcceptTaxi"),         state="*")
        dp.register_callback_query_handler(self.menu_new_order, lambda x: x.data.startswith("orderAcceptDelivery"),     state="*")
        dp.register_callback_query_handler(self.menu_new_order, lambda x: x.data.startswith("orderAcceptTruck"),     state="*")










