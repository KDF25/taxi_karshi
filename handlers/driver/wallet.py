from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToDeleteNotFound


from dispatcher import bot_driver as bot
from handlers.driver.checking_online import checking_online
from keyboards.inline.driver.inline import InlineDriverData
from looping import pg
from text.driver.formWallet import FormWalletDriver
from text.language.main import Text_main
from text.language.ru import Ru_language as Model


Txt = Text_main()


class WalletDriver(StatesGroup):

    wallet_level1 = State()
    wallet_level2 = State()
    wallet_level3 = State()
    wallet_level4 = State()
    wallet_level5 = State()

    async def menu_wallet(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level1.set()
        async with state.proxy() as data:
            form = FormWalletDriver(data=data)
            inline = InlineDriverData(language=data.get('lang'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=await form.wallet_form(), reply_markup=await inline.menu_balance())
            await call.answer()

    async def menu_amount(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level2.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            inline = InlineDriverData(language=data.get('lang'))
        with suppress(MessageNotModified):
            await bot.edit_message_text(chat_id=call.from_user.id, text=Lang.wallet.payment,
                                        message_id=call.message.message_id, reply_markup=await inline.menu_cash())
        await call.answer()

    async def menu_pay_way(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level3.set()
        async with state.proxy() as data:
            dta = call.data.split('_')
            if dta[0] == 'cash':
                data['cash'] = int(call.data.split('_')[1])
            form = FormWalletDriver(data=data)
            inline = InlineDriverData(language=data.get('lang'))
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=await form.pay_way_form(), reply_markup=await inline.menu_pay_way())
            await call.answer()

    async def menu_payme(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level4.set()
        async with state.proxy() as data:
            if call.data == 'Payme':
                data['type'] = call.data
            form = FormWalletDriver(data=data)
            inline = InlineDriverData(language=data.get('lang'))
            data["pay_id"] = await pg.wallet_pay(driver_id=call.from_user.id, cash=data["cash"], type_of_payment='Payme', status=False)
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            text=await form.payment_form(), reply_markup=await inline.payme_url())
            await call.answer()

    async def menu_click(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level4.set()
        async with state.proxy() as data:
            if call.data == 'Click':
                data['type'] = call.data
            form = FormWalletDriver(data=data)
            inline = InlineDriverData(language=data.get('lang'))
            data["pay_id"] = await pg.wallet_pay(driver_id=call.from_user.id, cash=data["cash"], type_of_payment='Click', status=False)
            text = await form.payment_form()
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                            reply_markup=await inline.click_url())
            await call.answer()

    async def menu_paynet(self, call: types.CallbackQuery, state: FSMContext):
        await self.wallet_level4.set()
        async with state.proxy() as data:
            if call.data == 'Paynet':
                data['type'] = call.data
            form = FormWalletDriver(data=data)
            inline = InlineDriverData(language=data.get('lang'))
            data["pay_id"] = await pg.wallet_pay(driver_id=call.from_user.id, cash=data["cash"], type_of_payment='Paynet', status=False)
            text = await form.payment_form()
            with suppress(MessageNotModified):
                await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                            reply_markup=await inline.click_url())
            await call.answer()


    async def menu_payed(self, call: types.CallbackQuery, state: FSMContext):
        await state.set_state("MenuDriver:menu_level1")
        async with state.proxy() as data:
            await pg.update_wallet_pay(pay_id=data['pay_id'])
            await pg.update_cash_to_wallet(pay_id=data['pay_id'])
            Lang: Model = Txt.language[data.get('lang')]
            with suppress(MessageToDeleteNotFound):
                await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_message(chat_id=call.from_user.id, text=Lang.wallet.accept,
                                   reply_markup=await checking_online(call.from_user.id, data.get('lang')))

    def register_handlers(self, dp: Dispatcher):
        dp.register_callback_query_handler(self.menu_wallet, text="back",                                               state=self.wallet_level2)

        dp.register_callback_query_handler(self.menu_amount, lambda x: x.data and x.data.startswith("balance"),         state=self.wallet_level1)
        dp.register_callback_query_handler(self.menu_amount, text="back",                                               state=self.wallet_level3)

        dp.register_callback_query_handler(self.menu_pay_way, lambda x: x.data.startswith("cash"),                      state=self.wallet_level2)
        dp.register_callback_query_handler(self.menu_pay_way, text="back",                                              state=self.wallet_level4)

        dp.register_callback_query_handler(self.menu_payme, text='Payme',                                               state=self.wallet_level3)
        dp.register_callback_query_handler(self.menu_click, text='Click',                                               state=self.wallet_level3)
        dp.register_callback_query_handler(self.menu_paynet, text='Paynet',                                             state=self.wallet_level3)

        dp.register_callback_query_handler(self.menu_payed, text='payed',                                               state=self.wallet_level4)








