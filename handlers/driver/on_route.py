import datetime
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound
from geopy.distance import geodesic

from dispatcher import bot_driver as bot, bot_client
from datetime_now import dt_now
from handlers.driver.order_data import OrderDataDriver
from keyboards.inline.client.inline import InlineClient
from keyboards.reply.client import ReplyClient
from keyboards.reply.driver import ReplyDriver
from looping import pg
from text.driver.formMenuDriver import FormMenuDriver
from text.function.function import TextFunc
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()
func = TextFunc()
order_data = OrderDataDriver()


class OnRouteDriver(StatesGroup):
    menu_level_onSpot = State()
    menu_level_start_trip = State()
    menu_level_waiting = State()
    menu_level_letsGo = State()

    async def menu_onSpot(self, message:  types.Message, state: FSMContext):
        async with state.proxy() as data:
            await self._get_order_data(message, data)
            data["location_driver"] = {'latitude': float(message.location.latitude), 'longitude': float(message.location.longitude)}
            distance = await self._location(data["location"], data["location_driver"])
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            print(data)
            if (distance < 100 and data['type'] in ["standard", "comfort"]) or data['type'] not in ["standard", "comfort"]:
                await self.onSpot_driver(message, state)
                await self._onSpot_client(data)
            else:
                Lang: Model = Txt.language[data.get('lang')]
                await bot.send_message(chat_id=message.from_user.id, text=Lang.alert.driver.orderDistance)

    async def onSpot_driver(self, message:  types.Message, state: FSMContext):
        await self.menu_level_onSpot.set()
        async with state.proxy() as data:
            await self._get_order_data(message, data)
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await bot.send_message(chat_id=message.from_user.id, text=Lang.start_driver.onSpot, reply_markup=await reply.menu_start_trip())

    @staticmethod
    async def _get_order_data(message:  types.Message, data: dict):
        await func.personal_data(message, data)
        await order_data.get_accept_order(message, data)

    @staticmethod
    async def _onSpot_client(data: dict):
        form = FormMenuDriver(language=data.get('lang_client'), data=data)
        await bot_client.send_location(chat_id=data['client_id'], latitude=data['location_driver']['latitude'], longitude=data['location_driver']['longitude'])
        await bot_client.send_message(chat_id=data['client_id'], text=await form.menu_onSpot_client())

    async def menu_start_trip(self, message:  types.Message, state: FSMContext):
        await self.\
            start_trip_driver(message, state)
        await self._start_trip_client(await state.get_data())

    async def start_trip_driver(self, message:  types.Message, state: FSMContext):
        await self.menu_level_start_trip.set()
        async with state.proxy() as data:
            data['start_time'] = datetime.datetime.strftime(dt_now.now(), "%d.%m.%y %H:%M:%S") if data.get('start_time') is None else data['start_time']
            data['waiting_time'] = 0 if data.get('waiting_time') is None else data['waiting_time']
            await pg.finish_accept_order(fee=0, waiting_fee=0, orders_accepted_id=data['order_accept_id'], datetime_arrive=data['start_time'])
            await pg.update_on_route_status(driver_id=message.from_user.id, status=False)
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await bot.send_message(chat_id=message.from_user.id, text=Lang.start_driver.start, reply_markup=await reply.menu_finish_trip())
            print(data)

    @staticmethod
    async def _start_trip_client(data: dict):
        Lang: Model = Txt.language[data.get('lang_client')]
        await bot_client.send_message(chat_id=data['client_id'], text=Lang.start_driver.client.start)

    async def menu_waiting(self, message:  types.Message, state: FSMContext):
        await self._waiting_driver(message, state)

    async def _waiting_driver(self, message:  types.Message, state: FSMContext):
        await self.menu_level_waiting.set()
        async with state.proxy() as data:
            data['star_waiting_time'] = datetime.datetime.strftime(dt_now.now(), "%d.%m.%y %H:%M:%S") \
                if data.get('star_waiting_time') is None else data['star_waiting_time']
            await self._timedelta_waiting(data)
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await bot.send_message(chat_id=message.from_user.id, text=Lang.start_driver.waiting, reply_markup=await reply.menu_waiting_trip())

    async def menu_letsGo(self, message:  types.Message, state: FSMContext):
        await self.menu_level_letsGo.set()
        async with state.proxy() as data:
            await self._timedelta_waiting(data)
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await bot.send_message(chat_id=message.from_user.id, text=Lang.start_driver.letsGo, reply_markup=await reply.menu_finish_trip())

    @staticmethod
    async def _timedelta_waiting(data):
        data['end_waiting_time'] = datetime.datetime.strftime(dt_now.now(), "%d.%m.%y %H:%M:%S")
        time = datetime.datetime.strptime(data['star_waiting_time'], "%d.%m.%y %H:%M:%S")
        delta = dt_now.now() - time
        data['waiting_time'] = round(delta.total_seconds() / 60, 2) + data.get('waiting_time', 0)

    async def menu_finish(self, message:  types.Message, state: FSMContext):
        await state.set_state('MenuDriver:menu_level1')
        async with state.proxy() as data:
            data["location_finish"] = {'latitude': float(message.location.latitude), 'longitude': float(message.location.longitude)}
            await self._data(data)
            await self._send_driver(data)
            await self._send_client(data)

    async def _data(self, data: dict):
        data['distance'] = await self._location(data["location"], data["location_finish"])
        await self._timedelta(data)
        await self._all_cash(data)
        await pg.finish_accept_order(fee=data['cash_total'], waiting_fee=data['cash_waiting'], status=True,
                                     orders_accepted_id=data['order_accept_id'], datetime_arrive=data['start_time'])
        await self._update_wallet(data)
        data['new_cashback'] = int(data['cash_total'] * Txt.money.client.cashback)
        data['cashback'] = await pg.update_client_cashback(client_id=data['client_id'],
                                                           cashback=int(data['new_cashback']))

    @staticmethod
    async def _send_driver(data: dict):
        form = FormMenuDriver(language=data.get('lang'), data=data)
        reply = ReplyDriver(language=data.get('lang'))
        await bot.send_message(chat_id=data['driver_id'], text=await form.menu_finish_driver(), reply_markup=await reply.start_online())

    @staticmethod
    async def _send_client(data: dict):
        form = FormMenuDriver(language=data.get('lang_client'), data=data)
        reply = ReplyClient(language=data.get('lang_client'))
        await bot_client.send_message(chat_id=data['client_id'], text=await form.menu_finish_client(),
                                      reply_markup=await reply.main_menu())
        if data['cashback'] >= Txt.money.client.min_cashback:
            inline = InlineClient(language=data.get('lang_client'), order_id=data['order_accept_id'])
            await bot_client.send_message(chat_id=data['client_id'], text=await form.menu_pay_cashback(),
                                          reply_markup=await inline.menu_pay_cashback())

    @staticmethod
    async def _location(location_a: dict, location_b: dict):
        location_a = (location_a['latitude'], location_a['longitude'])
        location_b = (location_b['latitude'], location_b['longitude'])
        distance = round(geodesic(location_a, location_b).meters)
        return distance

    @staticmethod
    async def _all_cash(data):
        data['cash_time'] = await func.cost_distance(data['distance'], data['type'])
        data['cash_waiting'] = await func.cost_time(data['waiting_time'], data['type'])
        data['cash_total'] = data['cash_time'] + data['cash_waiting']

    @staticmethod
    async def _timedelta(data):
        data['end_time'] = datetime.datetime.strftime(dt_now.now(), "%d.%m.%y %H:%M:%S")
        time = datetime.datetime.strptime(data['start_time'], "%d.%m.%y %H:%M:%S")
        delta = dt_now.now() - time
        data['time'] = round(delta.total_seconds() / 60, 2) - data['waiting_time']

    @staticmethod
    async def _update_wallet(data: dict):
        min_price = Txt.money.driver.order_min_price
        commission = int(data['cash_total'] * Txt.money.driver.commission)
        price = commission - min_price if commission > min_price else 0
        wallet = await pg.select_every_wallet(driver_id=data['driver_id'])
        data['wallet'] = [i for i in wallet]
        data['cash_commission'] = commission if commission > min_price else min_price
        await func.change_wallet(data, price)
        await pg.update_driver_wallet_accept(driver_id=data.get('driver_id'), wallet=data['wallet'])

    def register_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.menu_onSpot, content_types='location',                                         state="NewOrderDriver:menu_level_new_order")
        dp.register_message_handler(self.menu_start_trip, text=Txt.driver.onSpot.start,                                 state='*')
        dp.register_message_handler(self.menu_waiting, text=Txt.driver.onSpot.waiting,                                  state='*')
        dp.register_message_handler(self.menu_letsGo, text=Txt.driver.onSpot.letsGo,                                    state='*')
        dp.register_message_handler(self.menu_finish, content_types='location',                                         state=[self.menu_level_onSpot, self.menu_level_start_trip,
                                                                                                                               self.menu_level_letsGo, "*"])




