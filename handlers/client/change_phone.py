from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from dispatcher import bot_client as bot
from filters.client import IsPhone
from handlers.client.menu import MenuClient
from keyboards.inline.common.common import Start
from keyboards.reply.client import ReplyClient
from looping import pg
from text.client.formPassenger import FormPassenger
from text.language.main import Text_main

Txt = Text_main()
inline = Start()


class ChangePhoneClient(StatesGroup):
    phone_level1 = State()

    async def menu_phone(self, message: types.Message, state: FSMContext):
        await self.phone_level1.set()
        async with state.proxy() as data:
            phone = await pg.select_phone(user_id=message.from_user.id)
            data["phone"] = phone if phone is not None else "..."
            reply = ReplyClient(language=data.get('lang'))
            form = FormPassenger(data=data)
        await bot.send_message(chat_id=message.from_user.id, text=await form.menu_phone(),
                               reply_markup=await reply.menu_phone())

    async def menu_get_phone(self, message: types.Message, state: FSMContext):
        await pg.update_phone(phone=await self._phone(message=message), user_id=message.from_user.id)
        menu = MenuClient()
        await menu.main_menu(message=message, state=state)

    @staticmethod
    async def _phone(message: types.Message):
        if message.text is None:
            return message.contact.phone_number
        else:
            return message.text

    def register_handlers(self, dp: Dispatcher):

        dp.register_message_handler(self.menu_phone, text=Txt.client.menu.phone,                                        state="*")
        dp.register_message_handler(self.menu_get_phone, IsPhone(), content_types=['text'],                             state=self.phone_level1)
        dp.register_message_handler(self.menu_get_phone, content_types=["contact"],                                     state=self.phone_level1)


