from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageNotModified

from dispatcher import bot_driver as bot
from keyboards.inline.driver.inline import InlineDriverData
from keyboards.reply.driver import ReplyDriver
from looping import pg
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class OnlineDriver(StatesGroup):
    start = State()

    async def menu_change_spot(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            await self._check(call, data)
            inline = InlineDriverData(language=data.get('lang'), spots=data['spots'], delivery=data['delivery'], truck=data['truck'])
            Lang: Model = Txt.language[data.get('lang')]
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, text=Lang.tarif.driver.spots,
                                            message_id=call.message.message_id, reply_markup=await inline.menu_spots())
            await call.answer()

    async def _check(self, call: types.CallbackQuery, data):
        if call.data == "delivery" and data['car_type'] != "truck":
            await self._check_delivery(data)

        elif call.data == "truck" and data['car_type'] == "truck":
            await self._check_truck(data)

        elif call.data == "truck" and data['car_type'] != "truck":
            Lang: Model = Txt.language[data.get('lang')]
            await call.answer(show_alert=True, text=Lang.alert.driver.onlyNoTruck)

        elif data.get('car_type') != "truck":
            await self._check_spot(data, int(call.data.split('_')[1]))

        else:
            Lang: Model = Txt.language[data.get('lang')]
            await call.answer(show_alert=True, text=Lang.alert.driver.onlyTruck)

    @staticmethod
    async def _check_delivery(data):
        data["delivery"] = True if data["delivery"] is False else False

    @staticmethod
    async def _check_truck(data):
        data["truck"] = True if data["truck"] is False else False

    @staticmethod
    async def _check_spot(data, spot):
        if spot not in data['spots']:
            data['spots'].append(spot)
        else:
            data['spots'].remove(spot)

    async def menu_accept(self, call: types.CallbackQuery, state: FSMContext):
        print(call.data,await state.get_data())
        async with state.proxy() as data:
            if len(data['spots']) == 0 and data['delivery'] is False and data['truck'] is False:
                await self._empty_spot(call, state)
            else:
                await self._accept(call, state)

    @staticmethod
    async def _empty_spot(call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            await call.answer(show_alert=True, text=Lang.alert.driver.emptySpots)

    @staticmethod
    async def _accept(call: types.CallbackQuery, state: FSMContext):
        await state.set_state("MenuDriver:menu_level1")
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            await pg.update_drivers_status(driver_id=call.from_user.id, status=True)
            await pg.new_route_driver(driver_id=call.from_user.id, spots=data['spots'],
                                      delivery=data['delivery'], truck=data['truck'])
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text=Lang.online.accept, reply_markup=await reply.start_online())

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_change_spot, lambda x: x.data.startswith("spot"),                  state=self.start)
        dp.register_callback_query_handler(self.menu_change_spot, text=["delivery", "truck"],                           state=self.start)
        dp.register_callback_query_handler(self.menu_accept, text="accept",                                             state=self.start)









