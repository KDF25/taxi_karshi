import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from dispatcher import bot_client as bot, bot_driver
from filters.client import IsPhone
from keyboards.inline.client.inline import InlineClient
from keyboards.reply.client import ReplyClient
from looping import pg
from text.client.formTruck import FormTruck
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class TruckClient(StatesGroup):

    truck_level1 = State()
    truck_level2 = State()
    truck_level3 = State()
    truck_level4 = State()
    truck_level5 = State()
    phone_level1 = State()

    async def menu_choose_type(self, message: types.Message, state: FSMContext):
        await self.truck_level2.set()
        async with state.proxy() as data:
            print(data)
            Lang: Model = Txt.language[data.get('lang')]
            data["type"] = await pg.car_subtype_to_id(car_subtype=message.text, language=data['lang'])
            reply = ReplyClient(language=data.get('lang'))
        await bot.send_message(chat_id=message.from_user.id, text=Lang.client.location, reply_markup=await reply.menu_location())

    async def menu_comment(self, message: types.Message, state: FSMContext):
        await self.truck_level3.set()
        async with state.proxy() as data:
            data["location"] = {'latitude': float(message.location.latitude), 'longitude': message.location.longitude}
            reply = ReplyClient(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Lang.client.comment, reply_markup=await reply.menu_comment())

    async def menu_check_phone(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            await self._comment(message=message, data=data)
        condition: bool = await pg.exist_phone_client(user_id=message.from_user.id)
        if condition:
            await self.menu_find(message=message, state=state)
        else:
            await self.menu_phone(message=message, state=state)

    @staticmethod
    async def _comment(message: types.Message, data: dict):
        Lang: Model = Txt.language[data.get('lang')]
        if message.text != Lang.buttons.client.taxi.comment:
            data['comment'] = message.text

    async def menu_phone(self, message: types.Message, state: FSMContext):
        await self.phone_level1.set()
        async with state.proxy() as data:
            reply = ReplyClient(language=data.get('lang'))
            Lang: Model = Txt.language[data.get('lang')]
        await bot.send_message(chat_id=message.from_user.id, text=Lang.client.phone, reply_markup=await reply.menu_phone())

    async def menu_get_phone(self, message: types.Message, state: FSMContext):
        await pg.update_phone(phone=await self._phone(message=message), user_id=message.from_user.id)
        await self.menu_find(message=message, state=state)

    @staticmethod
    async def _phone(message: types.Message):
        if message.text is None:
            return message.contact.phone_number
        else:
            return message.text

    async def menu_find(self, message: types.Message, state: FSMContext):
        await self.truck_level3.set()
        async with state.proxy() as data:
            await self._data(message, data)
            reply = ReplyClient(language=data.get('lang'))
            form = FormTruck(data=data)
        await bot.send_message(chat_id=message.from_user.id, text=await form.menu_find(),
                               reply_markup=await reply.main_menu())
        await self._mailing(data=data)
        await self._delay(data=data)

    @staticmethod
    async def _data(message: types.Message, data: dict):
        data["phone"] = await pg.select_phone(user_id=message.from_user.id)
        data['user_id'] = message.from_user.id
        data['spot'] = await pg.select_spot(location=data['location'])
        data['order_id'] = await pg.new_order_client(client_id=message.from_user.id, order_type=data['type'],
                                                     location=data['location'], comment=data.get('comment'),
                                                     spot=data['spot'], payment_type="cash")

    @staticmethod
    async def _mailing(data: dict):
        drivers = await pg.select_drivers_trucks(_type=data['type'])
        if len(drivers) != 0:
            for driver_id in drivers:
                language = await pg.select_language_driver(user_id=driver_id[0])
                form = FormTruck(language=language, data=data)
                inline = InlineClient(language=language, order_id=data['order_id'])
                await bot_driver.send_message(chat_id=driver_id[0], reply_markup=await inline.menu_accept_truck(),
                                              text=await form.menu_mailing())
            await asyncio.sleep(5 * 60)

    @staticmethod
    async def _delay(data: dict):
        condition = await pg.check_order_accept(order_id=data['order_id'])
        if condition is None:
            Lang: Model = Txt.language[data.get('lang')]
            await bot.send_message(chat_id=data['user_id'], text=Lang.client.notFound)
            await pg.update_order(order_client_id=data['order_id'], status=False)

    def register_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.menu_choose_type, text=Txt.client.truck.small +
                                                                Txt.client.truck.medium + Txt.client.truck.big,         state=self.truck_level1)

        dp.register_message_handler(self.menu_comment, content_types='location',                                        state=self.truck_level2)
        dp.register_message_handler(self.menu_check_phone, content_types=['text'],                                      state=self.truck_level3)
        dp.register_message_handler(self.menu_get_phone,  IsPhone(), content_types=['text'],                            state=self.phone_level1)
        dp.register_message_handler(self.menu_get_phone,  content_types=["contact"],                                    state=self.phone_level1)
