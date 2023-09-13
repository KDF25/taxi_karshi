from contextlib import suppress
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from dispatcher import bot_driver as bot
from handlers.driver.checking_online import checking_online
from handlers.driver.on_route import OnRouteDriver
from handlers.driver.registration_taxi import RegistrationDriverCar
from keyboards.inline.common.common import Start
from keyboards.inline.driver.inline import InlineDriverData
from keyboards.reply.driver import ReplyDriver
from looping import pg
from text.driver.formPersonalData import FormPersonalData
from text.driver.formRegistration import FormRegistration
from text.driver.formWallet import FormWalletDriver
from text.function.function import TextFunc
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()
start = Start()
func = TextFunc()
on_route = OnRouteDriver()


class MenuDriver(StatesGroup):
    registration = State()
    menu_level1 = State()
    menu_level2 = State()
    phone_level1 = State()
    settings_level1 = State()
    settings_level2 = State()

    @staticmethod
    async def void(call: types.CallbackQuery):
        await call.answer()

    async def command_start(self, message: types.Message, state: FSMContext):
        exist = await pg.exist_driver(message.from_user.id)
        exist_lang = await pg.exist_lang_driver(message.from_user.id)
        exist_client = await pg.exist_client_driver(message.from_user.id)
        if await pg.select_active_order_driver(driver_id=message.from_user.id) is not None:
            await self._get_current_state(message, state)
        elif exist is True and exist_lang is True:
            await pg.block_status_driver(user_id=message.from_user.id, status=True)
            await state.reset_data()
            await self._greeting_client(message=message, state=state)
            await self.menu_level1.set()
        elif exist_client is False or exist_lang is False:
            await self._new_user(message=message, exist_client=exist_client)
        elif exist is False and exist_client is True:
            registration = RegistrationDriverCar()
            await registration.menu_start(message=message, state=state)

    @staticmethod
    async def _get_current_state(message: types.Message, state: FSMContext):
        current_state = await state.get_state()

        if current_state == 'OnRouteDriver:menu_level_onSpot':
            await on_route.onSpot_driver(message, state)
        elif current_state == 'OnRouteDriver:menu_level_waiting':
            await on_route.menu_waiting(message, state)
        elif current_state == 'OnRouteDriver:menu_level_letsGo':
            await on_route.menu_letsGo(message, state)
        elif current_state == 'OnRouteDriver:menu_level_start_trip':
            await on_route.start_trip_driver(message, state)

        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id-1)

    async def _new_user(self, message: types.Message, exist_client: bool):
        await bot.send_message(chat_id=message.from_user.id, text=Txt.choose_language, reply_markup=await start.choose_language())
        if exist_client is False:
            await self._rec_client(message=message)
            await self.registration.set()

    @staticmethod
    async def _rec_client(message: types.Message):
        user_id = message.from_user.id
        name = message.from_user.first_name
        username = message.from_user.username
        await pg.first_rec_in_driver(user_id=user_id, name=name, username=username, status=True)

    @staticmethod
    async def _greeting_client(message, state: FSMContext):
        async with state.proxy() as data:
            data['lang'] = await pg.select_language_driver(user_id=message.from_user.id)
            Lang: Model = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Lang.start.greeting,
                               reply_markup=await checking_online(message.from_user.id, data.get('lang')))

    @staticmethod
    async def menu_choose_language(call: types.callback_query, state: FSMContext):
        async with state.proxy() as data:
            await pg.update_language_driver(language=call.data, user_id=call.from_user.id)
            data['lang'] = call.data
        registration = RegistrationDriverCar()
        await registration.menu_start(message=call, state=state)

    async def main_menu(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.menu_level1.set()
        async with state.proxy() as data:
            await state.set_data(data={"lang": data.get('lang')})
            Lang: Model = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Lang.menu.client.menu,
                               reply_markup=await checking_online(message.from_user.id, data.get('lang')))

    async def menu_settings(self, message: types.Message, state: FSMContext):
        await self.settings_level1.set()
        async with state.proxy() as data:
            reply = ReplyDriver(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Lang.menu.driver.settings, reply_markup=await reply.menu_settings())

    @staticmethod
    async def menu_about_us(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            form = FormRegistration(data=data)
            await bot.send_message(chat_id=message.from_user.id, text=await form.menu_about_us())

    @staticmethod
    async def menu_feedback(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            await bot.send_message(chat_id=message.from_user.id, text=Lang.feedback.feedback)

    @staticmethod
    async def menu_personal_data(message:  types.Message, state: FSMContext):
        await state.set_state('PersonalCabinet:change_data')
        async with state.proxy() as data:
            await func.personal_data(message, data)
            data['color'] = await pg.id_to_color(id=data['color_id'], language=data['lang'])
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            form = FormPersonalData(data=data)
            inline = InlineDriverData(language=data.get('lang'))
        await bot.send_message(chat_id=message.from_user.id, text=Lang.buttons.personal_cabinet.data,
                               reply_markup=await reply.main_menu())
        await bot.send_message(chat_id=message.from_user.id, text=await form.personal_data_form(),
                               reply_markup=await inline.menu_personal_data())

    async def menu_language(self, message: types.Message, state: FSMContext):
        await self.settings_level2.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            await bot.send_message(chat_id=message.from_user.id, text=Lang.information.language,
                                   reply_markup=await reply.menu_language())

    async def menu_online(self, message:  types.Message, state: FSMContext):
        await self._check_balance(message, state)

    @staticmethod
    async def _online(message:  types.Message, state: FSMContext):
        await state.set_state("OnlineDriver:start")
        async with state.proxy() as data:
            await func.personal_data(message, data)
            data['spots'] = []
            data['delivery'] = False
            data['truck'] = False
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            inline = InlineDriverData(language=data.get('lang'), spots=data['spots'])
        await bot.send_message(chat_id=message.from_user.id, text=Lang.menu.driver.online, reply_markup=await reply.main_menu())
        await bot.send_message(chat_id=message.from_user.id, text=Lang.tarif.driver.spots, reply_markup=await inline.menu_spots())

    async def _check_balance(self, message:  types.Message, state: FSMContext):
        driver_id = message.from_user.id
        wallet = await pg.select_wallets(driver_id=driver_id)
        wallet = [i for i in wallet]
        if sum(wallet) >= Txt.money.driver.order_min_price:
            await self._online(message, state)
        else:
            await self._alert(message, state)
            await self.menu_wallet(message, state)

    @staticmethod
    async def _alert(message:  types.Message, state: FSMContext):
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            await bot.send_message(chat_id=message.from_user.id, text=Lang.alert.driver.notEnoughMoney)

    async def menu_offline(self, message:  types.Message, state: FSMContext):
        await self.menu_level1.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            await pg.update_drivers_status(driver_id=message.from_user.id, status=False)
            await pg.cancel_route_driver(driver_id=message.from_user.id)
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await bot.send_message(chat_id=message.from_user.id, text=Lang.offline.reject, reply_markup=await reply.start_offline())

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

        await pg.update_language_driver(language=language, user_id=message.from_user.id)
        return language

    async def menu_wallet(self, message:  types.Message, state: FSMContext):
        await state.set_state("WalletDriver:wallet_level1")
        async with state.proxy() as data:
            await self._get_wallets(data, message)
            Lang: Model = Txt.language[data.get('lang')]
            form = FormWalletDriver(data=data)
            inline = InlineDriverData(language=data.get('lang'))
            reply = ReplyDriver(language=data.get('lang'))
            await bot.send_message(chat_id=message.from_user.id, reply_markup=await reply.main_menu(), text=Lang.menu.driver.wallet)
            await bot.send_message(chat_id=message.from_user.id, text=await form.wallet_form(),  reply_markup=await inline.menu_balance())

    @staticmethod
    async def _get_wallets(data: dict, message: types.Message):
        data['driver_id'] = message.from_user.id
        wallet = await pg.select_wallets(driver_id=data['driver_id'])
        data['wallet'] = [i for i in wallet]

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.void, text=["void"],                                                    state="*")
        dp.register_message_handler(self.command_start, commands="start",                                               state='*')

        dp.register_callback_query_handler(self.menu_choose_language, text=['rus', 'ozb', 'uzb'],                       state="*")
        dp.register_message_handler(self.main_menu, text=Txt.driver.menu.menu,                                          state='*')
        dp.register_message_handler(self.menu_settings, text=Txt.driver.menu.settings,                                  state=[self.menu_level1, '*'])
        dp.register_message_handler(self.menu_online, text=Txt.driver.menu.online,                                      state=[self.menu_level1, '*'])
        dp.register_message_handler(self.menu_offline, text=Txt.driver.menu.offline,                                    state=[self.menu_level1, '*'])

        dp.register_message_handler(self.menu_personal_data, text=Txt.information.personalData,                         state=self.settings_level1)
        dp.register_message_handler(self.menu_feedback, text=Txt.information.feedback,                                  state=self.settings_level1)
        dp.register_message_handler(self.menu_about_us, text=Txt.information.about_us,                                  state=self.settings_level1)
        dp.register_message_handler(self.menu_language, text=Txt.information.language,                                  state=self.settings_level1)

        dp.register_message_handler(self.menu_change_language, text=Txt.settings.language,                              state=self.settings_level2)

        dp.register_message_handler(self.menu_wallet, text=Txt.driver.menu.wallet,                                      state="*")





