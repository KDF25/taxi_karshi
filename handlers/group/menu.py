from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from dispatcher import bot_driver as bot, moderation_chat_id
from looping import pg
from text.language.main import Text_main

Txt = Text_main()


class MenuGroup(StatesGroup):

    @staticmethod
    async def menu_accept(call: types.callback_query, state: FSMContext):
        id, driver_id = await pg.update_wallet_pay_status(status=True, pay_id=int(call.data.split('_')[1]))
        tarif_end = await pg.update_wallet_pay_status2(driver_id=driver_id, current_tarif=id)
        form = FormActivity(id=id, language=await pg.select_language_driver(driver_id))
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=moderation_chat_id, message_id=call.message.message_id)
        await bot.send_message(chat_id=driver_id, text=await form.menu_accept(tarif_end))

    @staticmethod
    async def menu_reject(call: types.callback_query):
        await pg.update_wallet_pay_status(status=False, pay_id=int(call.data.split('_')[1]))
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=moderation_chat_id, message_id=call.message.message_id)

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_accept, lambda x: x.data.startswith("paymentAccept"),              state="*")
        dp.register_callback_query_handler(self.menu_reject, lambda x: x.data.startswith("paymentReject"),              state="*")



