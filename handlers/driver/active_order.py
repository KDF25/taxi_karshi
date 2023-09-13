from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound

from dispatcher import bot_driver as bot, bot_client
from handlers.driver.checking_online import checking_online
from keyboards.inline.driver.inline import InlineDriverData
from looping import pg
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class ActiveOrderDriver(StatesGroup):
    @staticmethod
    async def menu_cancel(call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            inline = InlineDriverData(order_id=int(call.data.split('_')[1]), language=data.get('lang'))
            with suppress(MessageNotModified, MessageToEditNotFound):
                await call.answer()
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=Lang.active_order.cancel, reply_markup=await inline.menu_delete_active_order())

    async def menu_delete(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            await self._delete_driver(call, data)
            await self._delete_client(data)

    @staticmethod
    async def _delete_driver(call: types.CallbackQuery, data: dict):
        await pg.update_order(order_client_id=int(call.data.split('_')[1]), status=False)
        await pg.update_on_route_status(driver_id=call.from_user.id, status=False)
        await pg.update_cancel_order(order_client_id=int(call.data.split('_')[1]), cancel_by="driver")
        Lang: Model = Txt.language[data.get('lang')]
        with suppress(MessageNotModified, MessageToEditNotFound):
            await call.answer()
            await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=Lang.active_order.delete)
        await bot.send_message(chat_id=call.from_user.id, text=Lang.menu.client.menu,
                               reply_markup=await checking_online(call.from_user.id, data.get('lang')))

    @staticmethod
    async def _delete_client(data):
        Lang: Model = Txt.language[data['lang_client']]
        await bot_client.send_message(chat_id=data['client_id'], text=Lang.active_order.delete_client)

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_cancel, lambda x: x.data.startswith("cancel"),                     state="*")
        dp.register_callback_query_handler(self.menu_delete, lambda x: x.data.startswith("delete"),                     state="*")
