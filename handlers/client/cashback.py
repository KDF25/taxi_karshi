import datetime
from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.utils.exceptions import MessageToDeleteNotFound

from dispatcher import bot_client as bot, bot_driver
from datetime_now import dt_now
from keyboards.reply.client import ReplyClient
from looping import pg
from text.client.formOrder import FormOrderClient
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class CashbackClient(StatesGroup):
    async def main_pay_cashback(self,  call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            await self._get_data(call, data)

    async def _get_data(self, call: types.CallbackQuery, data: dict):
        data['client_id'] = call.from_user.id
        data['message_id'] = call.message.message_id
        data['order_id'] = int(call.data.split('_')[1])
        data['cashback'] = await pg.select_client_cashback(client_id=data['client_id'])
        data['fee'], data['driver_id'], data['lang_driver'], datetime_finish = await pg.select_order_fee(order_id=data['order_id'])
        data['pay'] = data['fee'] - data['cashback'] if data['fee'] > data['cashback'] else 0
        data['lost_cashback'] = data['cashback'] if data['fee'] > data['cashback'] else data['fee']
        await self._checking_time(datetime_finish, data, call)
        print(data)

    async def _checking_time(self, time: datetime, data: dict,  call: types.CallbackQuery):
        if time + datetime.timedelta(minutes=Txt.money.client.cashback_time) > dt_now.now():
            await pg.update_client_cashback(client_id=data['client_id'], cashback=-data['lost_cashback'])
            await pg.update_driver_wallet_payment(driver_id=data['driver_id'], cash=data['lost_cashback'])
            await self._send_client(data)
            await self._send_driver(data)
        else:
            Lang: Model = Txt.language[data.get('lang')]
            await call.answer(show_alert=True, text=Lang.alert.driver.cashbackTime)

    @staticmethod
    async def _send_client(data: dict):
        with suppress(MessageToDeleteNotFound):
            await bot.delete_message(chat_id=data['client_id'], message_id=data['message_id'])
        reply = ReplyClient(language=data.get('lang'))
        form = FormOrderClient(language=data['lang'], data=data)
        await bot.send_message(chat_id=data['client_id'], text=await form.menu_finally(), reply_markup=await reply.start())

    @staticmethod
    async def _send_driver(data: dict):
        form = FormOrderClient(language=data['lang_driver'], data=data)
        await bot_driver.send_message(chat_id=data['driver_id'], text=await form.menu_finally_driver())

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.main_pay_cashback, lambda x: x.data.startswith("cashbackPay"),          state='*')
