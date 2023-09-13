from contextlib import suppress
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageNotModified, MessageToEditNotFound
from dispatcher import bot_driver as bot
from filters.driver import IsPhone, IsNumber
from keyboards.inline.driver.inline import InlineDriverData
from keyboards.reply.driver import ReplyDriver
from looping import pg
from text.driver.formPersonalData import FormPersonalData
from text.language.ru import Ru_language as Model
from text.language.main import Text_main

Txt = Text_main()


class PersonalCabinet(StatesGroup):
    personal_cabinet = State()

    change_data = State()
    _change_name = State()
    _change_phone = State()
    _change_auto = State()

    _change_model = State()
    _change_car_type = State()
    _change_car_subtype = State()
    _change_truck = State()

    _change_color = State()
    _change_number = State()

    async def menu_personal_data(self, message:  Union[types.Message, types.CallbackQuery], state: FSMContext):
        await self.change_data.set()
        async with state.proxy() as data:
            inline = InlineDriverData(language=data.get('lang'))
            form = FormPersonalData(data=data)
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=message.from_user.id, reply_markup=await inline.menu_personal_data(),
                                        message_id=message.message.message_id, text=await form.personal_data_form())
            await message.answer()

    async def menu_name(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_name.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, text=Lang.personal_cabinet.new_data,
                                            message_id=call.message.message_id)
                await call.answer()

    async def menu_get_name(self, message: types.Message, state: FSMContext):
        await self.change_data.set()
        async with state.proxy() as data:
            data['name'] = message.text
            await pg.update_drivers_name(driver_id=data.get('driver_id'), name=data.get('name'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await self._rec_data(message, data)

    @staticmethod
    async def _new_data(message: types.Message, data):
        Lang: Model = Txt.language[data.get('lang')]
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_message(chat_id=message.from_user.id, text=Lang.personal_cabinet.new_data_rec)

    async def menu_phone(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_phone.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            reply = ReplyDriver(language=data.get('lang'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text=Lang.personal_cabinet.new_data,
                                   reply_markup=await reply.menu_phone())

    async def menu_get_phone(self, message: types.Message, state: FSMContext):
        await self.change_data.set()
        async with state.proxy() as data:
            data["phone"] = await self._phone(message=message)
            await pg.update_phone(phone=data["phone"], user_id=message.from_user.id)
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            await self._rec_data(message, data)
            # await self._new_data(message, data)

    @staticmethod
    async def _phone(message: types.Message):
        if message.text is None:
            return message.contact.phone_number
        else:
            return message.text

    async def menu_auto(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_auto.set()
        async with state.proxy() as data:
            inline = InlineDriverData(language=data.get('lang'))
            form = FormPersonalData(data=data)
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, text=await form.change_car(),
                                            message_id=call.message.message_id, reply_markup=await inline.menu_auto())
                await call.answer()

    async def menu_cars(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_model.set()
        async with state.proxy() as data:
            inline = InlineDriverData(language=data.get('lang'))
            form = FormPersonalData(data=data)
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, text=await form.change_car(),
                                            message_id=call.message.message_id, reply_markup=await inline.menu_taxi())
                await call.answer()

    async def menu_get_cars(self, call: types.CallbackQuery, state: FSMContext):
        await self.change_data.set()
        async with state.proxy() as data:
            data['car'] = int(call.data.split('_')[1])
            await self._update_car(data)
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await self._rec_data(call, data)

    async def menu_car_type(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_car_type.set()
        async with state.proxy() as data:
            if call.data != "back":
                data['car_type'] = call.data
        with suppress(MessageToEditNotFound, MessageNotModified):
            inline = InlineDriverData(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Lang.registration.car_subtype, reply_markup=await inline.menu_car_subtype())

    async def menu_car_subtype(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_car_subtype.set()
        async with state.proxy() as data:
            if call.data != "back":
                data['car_subtype'] = call.data.split('_')[1]
        with suppress(MessageToEditNotFound, MessageNotModified):
            inline = InlineDriverData(language=data.get('lang'), car_type=data['car_type'], car_subtype=data['car_subtype'])
            Lang: Model = Txt.language[data.get('lang')]
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        text=Lang.registration.model, reply_markup=await inline.menu_trucks())

    async def menu_get_trucks(self, call: types.CallbackQuery, state: FSMContext):
        await self.change_data.set()
        async with state.proxy() as data:
            data['car'] = int(call.data.split('_')[1])
            await self._update_car(data)
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await self._rec_data(call, data)

    @staticmethod
    async def _update_car(data: dict):
        model, car_type, car_subtype = await pg.id_to_model(data.get("car"))
        data['model'] = model
        await pg.update_drivers_car(driver_id=data.get('driver_id'), car=data.get('car'), car_type=car_type, car_subtype=car_subtype)

    async def menu_color(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_color.set()
        async with state.proxy() as data:
            inline = InlineDriverData(language=data.get('lang'))
            form = FormPersonalData(data=data)
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, text=await form.change_car(),
                                            message_id=call.message.message_id, reply_markup=await inline.menu_color())
                await call.answer()

    async def menu_get_color(self, call: types.CallbackQuery, state: FSMContext):
        await self.change_data.set()
        async with state.proxy() as data:
            data['color_id'] = int(call.data.split('_')[1])
            data['color'] = await pg.id_to_color(id=data['color_id'], language=data['lang'])
            await pg.update_drivers_color(driver_id=data.get('driver_id'), color=data.get('color_id'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await self._rec_data(call, data)

    async def menu_number(self, call: types.CallbackQuery, state: FSMContext):
        await self._change_number.set()
        async with state.proxy() as data:
            form = FormPersonalData(data=data)
            inline = InlineDriverData(language=data.get('lang'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, text=await form.change_number(),
                                            message_id=call.message.message_id, reply_markup=await inline.menu_back())
                await call.answer()

    async def menu_get_number(self, message: types.Message, state: FSMContext):
        await self.change_data.set()
        async with state.proxy() as data:
            data['number'] = message.text
            await pg.update_drivers_color(driver_id=data.get('driver_id'), color=data.get('color'))
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id-1)
            await self._rec_data(message, data)

    @staticmethod
    async def _rec_data(message:  Union[types.Message, types.CallbackQuery], data: dict):
        reply = ReplyDriver(data.get('lang'))
        form = FormPersonalData(data=data)
        Lang: Model = Txt.language[data.get('lang')]
        inline = InlineDriverData(language=data.get('lang'))
        await bot.send_message(chat_id=message.from_user.id, text=Lang.personal_cabinet.new_data_rec,
                               reply_markup=await reply.main_menu())
        await bot.send_message(chat_id=message.from_user.id, text=await form.personal_data_form(),
                               reply_markup=await inline.menu_personal_data())

    def register_handlers(self, dp: Dispatcher):
        # personal data
        dp.register_callback_query_handler(self.menu_personal_data, text="back",                                        state=[self._change_auto, self._change_name, self._change_phone])

        dp.register_callback_query_handler(self.menu_name, text="name",                                                 state=self.change_data)
        dp.register_message_handler(self.menu_get_name, content_types="text",                                           state=self._change_name)

        dp.register_callback_query_handler(self.menu_auto, text="auto",                                                 state=self.change_data)
        dp.register_callback_query_handler(self.menu_auto, text="back",                                                 state=[self._change_model, self._change_color, self._change_number])

        dp.register_callback_query_handler(self.menu_cars, text="model",                                                state=self._change_auto)
        dp.register_callback_query_handler(self.menu_cars, text="back",                                                 state=self._change_car_type)
        dp.register_callback_query_handler(self.menu_get_cars, lambda x: x.data.startswith("car"),                      state=self._change_model)

        dp.register_callback_query_handler(self.menu_car_type, text="truck",                                            state=self._change_model)
        dp.register_callback_query_handler(self.menu_car_type, text="back",                                             state=self._change_car_subtype)

        dp.register_callback_query_handler(self.menu_car_subtype, lambda x: x.data.startswith("subtype"),               state=self._change_car_type)
        dp.register_callback_query_handler(self.menu_car_subtype, text="back",                                          state=self._change_truck)

        dp.register_callback_query_handler(self.menu_get_trucks, lambda x: x.data.startswith("truck"),                  state=self._change_car_subtype)

        dp.register_callback_query_handler(self.menu_color, text="colors",                                              state=self._change_auto)
        dp.register_callback_query_handler(self.menu_get_color, lambda x: x.data.startswith("color"),                   state=self._change_color)

        dp.register_callback_query_handler(self.menu_number, text="number",                                             state=self._change_auto)
        dp.register_message_handler(self.menu_get_number, IsNumber(), content_types="text",                             state=self._change_number)

        dp.register_callback_query_handler(self.menu_phone, text="phone",                                               state=self.change_data)

        dp.register_message_handler(self.menu_get_phone, IsPhone(), content_types=['text'],                             state=self._change_phone)
        dp.register_message_handler(self.menu_get_phone, content_types=["contact"],                                     state=self._change_phone)









