from contextlib import suppress
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound, MessageToEditNotFound

from dispatcher import bot_driver as bot
from filters.driver import IsNumber, IsPhone
from keyboards.inline.driver.inline import InlineDriverData
from keyboards.reply.driver import ReplyDriver
from looping import pg
from text.driver.formRegistration import FormRegistration
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class RegistrationDriverCar(StatesGroup):
    registration_level1 = State()
    registration_level2 = State()
    registration_level3 = State()
    registration_level4 = State()
    registration_level5 = State()
    registration_level6 = State()
    registration_level7 = State()
    registration_level8 = State()

    async def menu_start(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.registration_level1.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            if isinstance(message, types.Message):
                await bot.send_message(chat_id=message.from_user.id, text=Lang.registration.name)
            elif isinstance(message, types.CallbackQuery):
                with suppress(MessageToEditNotFound, MessageNotModified):
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.message_id,
                                                text=Lang.registration.name)
                    await message.answer()

    async def menu_name(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.registration_level2.set()
        async with state.proxy() as data:
            inline = InlineDriverData(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
            if isinstance(message, types.Message):
                data['name'] = message.text
                await bot.send_message(chat_id=message.from_user.id, text=Lang.registration.model,
                                       reply_markup=await inline.menu_taxi())
            elif isinstance(message, types.CallbackQuery):
                with suppress(MessageToEditNotFound, MessageNotModified):
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.message_id,
                                                text=Lang.registration.model, reply_markup=await inline.menu_taxi())
                await message.answer()

    async def menu_cars(self, call: types.CallbackQuery, state: FSMContext):
        await self.registration_level3.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == "car":
                data['car'] = int(dta[1])
        with suppress(MessageToEditNotFound, MessageNotModified):
            inline = InlineDriverData(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Lang.registration.color, reply_markup=await inline.menu_color())

    async def menu_color(self, call: types.CallbackQuery, state: FSMContext):
        await self.registration_level4.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            inline = InlineDriverData(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
            if dta[0] == "color":
                data['color'] = int(dta[1])
                with suppress(MessageToEditNotFound, MessageNotModified):
                    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                text=Lang.registration.number, reply_markup=await inline.menu_back())
            elif dta[0] == "back":
                with suppress(MessageToDeleteNotFound):
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id - 1)
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                await bot.send_message(chat_id=call.from_user.id, text=Lang.registration.number,
                                       reply_markup=await inline.menu_back())

    async def menu_number(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.registration_level5.set()
        if isinstance(message, types.Message):
            await self._number_accept(message=message, state=state)
        elif isinstance(message, types.CallbackQuery):
            await self._number_back(message=message, state=state)

    @staticmethod
    async def _number_accept(message: types.Message,  state: FSMContext):
        async with state.proxy() as data:
            data["number"] = message.text.upper()
            inline = InlineDriverData(language=data.get('lang'))
            reply = ReplyDriver(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
            await bot.send_message(chat_id=message.from_user.id, text=Lang.menu.driver.myPhone,  reply_markup=await reply.menu_phone())
            await bot.send_message(chat_id=message.from_user.id, text=Lang.registration.phone,
                                   reply_markup=await inline.menu_back())

    @staticmethod
    async def _number_back(message: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            inline = InlineDriverData(language=data.get('lang'))
            reply = ReplyDriver(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id-1)
        await bot.send_message(chat_id=message.from_user.id, text=Lang.menu.driver.myPhone, reply_markup=await reply.menu_phone())
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message.message_id)
        await bot.send_message(chat_id=message.from_user.id, text=Lang.registration.phone,
                               reply_markup=await inline.menu_back())
        await message.answer()

    async def menu_phone(self, message: Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.registration_level6.set()
        async with state.proxy() as data:
            data["phone"] = str(int(await self._phone(message=message)))
            await pg.update_phone(phone=data["phone"], user_id=message.from_user.id)
            inline = InlineDriverData(language=data.get('lang'))
            form = FormRegistration(data=data)
            await bot.send_message(chat_id=message.from_user.id, text=await form.agreement_car(),
                                   reply_markup=await inline.menu_agreement(), disable_web_page_preview=True)

    @staticmethod
    async def _phone(message: types.Message):
        if message.text is None:
            return message.contact.phone_number
        else:
            return message.text

    @staticmethod
    async def menu_registration(call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['user_id'] = call.from_user.id
            reply = ReplyDriver(language=data.get('lang'))
            form = FormRegistration(data=data)
            model, car_type, car_subtype = await pg.id_to_model(data.get("car"))
            await pg.first_rec_driver(driver_id=call.from_user.id, name=data.get("name"), username=data.get('username'),
                                      phone=data.get('phone'), car=data.get("car"), car_type=car_type,
                                      car_subtype=car_subtype, color=data.get('color'), number=data.get('number'),
                                      wallet=Txt.money.wallet.wallet)
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(chat_id=call.from_user.id, text=await form.finish(),
                               reply_markup=await reply.start_offline(), disable_web_page_preview=True)
        await state.set_state("MenuDriver:menu_level1")

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_start, text="back",                                                state=self.registration_level2)

        dp.register_message_handler(self.menu_name, content_types="text",                                               state=self.registration_level1)
        dp.register_callback_query_handler(self.menu_name, text="back",                                                 state=[self.registration_level3,
                                                                                                                               "RegistrationDriverTruck:registration_level1"])

        dp.register_callback_query_handler(self.menu_cars, lambda x: x.data.startswith("car"),                          state=self.registration_level2)
        dp.register_callback_query_handler(self.menu_cars, text="back",                                                 state=self.registration_level4)

        dp.register_callback_query_handler(self.menu_color, lambda x: x.data.startswith("color"),                       state=self.registration_level3)
        dp.register_callback_query_handler(self.menu_color, text="back",                                                state=self.registration_level5)

        dp.register_message_handler(self.menu_number, IsNumber(), content_types="text",                                 state=self.registration_level4)
        dp.register_callback_query_handler(self.menu_number, text="back",                                               state=self.registration_level6)

        dp.register_message_handler(self.menu_phone, IsPhone(), content_types=['text'],                                 state=self.registration_level5)
        dp.register_message_handler(self.menu_phone, content_types=["contact"],                                         state=self.registration_level5)

        dp.register_callback_query_handler(self.menu_registration, text="agree",                                        state=self.registration_level6)

