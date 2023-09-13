from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from dispatcher import bot_client as bot
from keyboards.inline.common.common import Start
from keyboards.reply.client import ReplyClient
from looping import pg
from text.client.formDelivery import FormDelivery
from text.client.formPassenger import FormPassenger
from text.client.formTruck import FormTruck
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()
inline = Start()


class MenuClient(StatesGroup):
    registration = State()
    menu_level1 = State()
    menu_level2 = State()

    @staticmethod
    async def void(call: types.CallbackQuery):
        await call.answer()

    async def command_start(self, message: types.Message, state: FSMContext):
        exist = await pg.exist_client(message.from_user.id)
        exist_lang = await pg.exist_lang(message.from_user.id)
        if exist is True and exist_lang is True:
            await pg.block_status(user_id=message.from_user.id, status=True)
            await state.reset_data()
            await self.start_client(message=message, state=state)
        elif exist is False or exist_lang is False:
            await self._new_user(message=message, exist=exist)

    async def _new_user(self, message: types.Message, exist: bool):
        await bot.send_message(chat_id=message.from_user.id, text=Txt.choose_language,
                               reply_markup=await inline.choose_language())
        if exist is False:
            await self._rec_client(message=message)
            await self.registration.set()

    @staticmethod
    async def _rec_client(message: types.Message):
        user_id = message.from_user.id
        name = message.from_user.first_name
        username = message.from_user.username
        await pg.first_rec_client(user_id=user_id, name=name, username=username, status=True)

    async def start_client(self, message: types.Message, state: FSMContext):
        await self._greeting_client(client_id=message.from_user.id, state=state)
        await self.menu_level1.set()

    @staticmethod
    async def _greeting_client(client_id, state: FSMContext):
        async with state.proxy() as data:
            data['lang'] = await pg.select_language(user_id=client_id)
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyClient(language=data.get('lang'))
        await bot.send_message(chat_id=client_id, text=Lang.start.greeting, reply_markup=await reply.start())

    async def menu_choose_language(self, call: types.callback_query, state: FSMContext):
        async with state.proxy() as data:
            await pg.update_language(language=call.data, user_id=call.from_user.id)
            data['lang'] = call.data
            reply = ReplyClient(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=Lang.start.client, reply_markup=await reply.start())
        await self.menu_level1.set()

    async def main_menu(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            await state.set_data(data={"lang": data.get('lang')})
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyClient(language=data.get('lang'))
        await bot.send_message(chat_id=message.from_user.id, text=Lang.menu.client.menu, reply_markup=await reply.start())
        await self.menu_level1.set()

    async def menu_language(self, message: types.Message, state: FSMContext):
        await self.menu_level2.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyClient(language=data.get('lang'))
            await bot.send_message(chat_id=message.from_user.id, text=Lang.information.language,
                                   reply_markup=await reply.menu_language())

    async def menu_change_language(self, message: types.Message, state: FSMContext):
        language = await self._change_language(message)
        async with state.proxy() as data:
            data['lang'] = language
        await self.main_menu(message, state)

    @staticmethod
    async def _change_language(message: types.Message):
        new_language = message.text
        if new_language == Txt.settings.rus:
            language = 'rus'
        elif new_language == Txt.settings.uzb:
            language = 'uzb'
        elif new_language == Txt.settings.ozb:
            language = 'ozb'
        else:
            return 'rus'
        await pg.update_language(language=language, user_id=message.from_user.id)
        return language

    @staticmethod
    async def menu_taxi(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['cashback'] = await pg.select_client_cashback(client_id=message.from_user.id)
            reply = ReplyClient(language=data.get('lang'))
            form = FormPassenger(data=data)
        await bot.send_message(chat_id=message.from_user.id, text=await form.menu_start(), reply_markup=await reply.menu_taxi())
        await state.set_state("TaxiClient:taxi_level1")

    @staticmethod
    async def menu_delivery(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['cashback'] = await pg.select_client_cashback(client_id=message.from_user.id)
            reply = ReplyClient(language=data.get('lang'))
            form = FormDelivery(data=data)
        await bot.send_message(chat_id=message.from_user.id, text=await form.menu_start(), reply_markup=await reply.menu_location())
        await state.set_state("DeliveryClient:delivery_level1")

    @staticmethod
    async def menu_truck(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['cashback'] = await pg.select_client_cashback(client_id=message.from_user.id)
            reply = ReplyClient(language=data.get('lang'))
            form = FormTruck(data=data)
        await bot.send_message(chat_id=message.from_user.id, text=await form.menu_start(), reply_markup=await reply.menu_truck())
        await state.set_state("TruckClient:truck_level1")

    @staticmethod
    async def menu_change_role(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Lang.driver.bot)

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.void, text=["void"],                                                    state="*")
        dp.register_message_handler(self.command_start, commands="start",                                               state='*')
        dp.register_callback_query_handler(self.menu_choose_language, text=['rus', 'ozb', 'uzb'],                       state=self.registration)
        dp.register_message_handler(self.main_menu, text=Txt.client.menu.menu,                                          state='*')
        dp.register_message_handler(self.menu_language, text=Txt.information.language,                                  state="*")
        dp.register_message_handler(self.menu_change_language, text=Txt.settings.language,                              state=self.menu_level2)

        dp.register_message_handler(self.menu_taxi, text=Txt.client.menu.taxi,                                          state=[self.menu_level1, "*"])
        dp.register_message_handler(self.menu_delivery, text=Txt.client.menu.delivery,                                  state=[self.menu_level1, "*"])
        dp.register_message_handler(self.menu_truck, text=Txt.client.menu.truck,                                        state=[self.menu_level1, "*"])
        dp.register_message_handler(self.menu_change_role, text=Txt.client.menu.change,                                 state=[self.menu_level1, "*"])


