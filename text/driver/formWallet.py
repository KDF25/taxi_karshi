from string import Template
from text.function.function import TextFunc
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()
func = TextFunc()


class FormWalletDriver:

    def __init__(self, data=None):
        self.__data = data
        self.__language = self.__data.get('lang')
        self.__Lang: Model = Txt.language[self.__data.get('lang')]

    async def wallet_form(self):
        await self._unpack_wallet()
        form = Template("<b>$id</b>: $driver_id\n\n"
                        "$wallet👇\n"
                        "<b>$main:</b> $wallet_main $sum\n"
                        "<b>$bonus:</b> $wallet_bonus $sum\n")
        form = form.substitute(id=self.__Lang.personal_cabinet.id, driver_id=self.__driver_id,
                               wallet=self.__Lang.personal_cabinet.wallet,
                               main=self.__Lang.personal_cabinet.common, wallet_main=self.__main,
                               bonus=self.__Lang.personal_cabinet.bonus, wallet_bonus=self.__bonus,
                               sum=self.__Lang.symbol.sum)
        return form

    async def _unpack_wallet(self):
        self.__driver_id = self.__data.get('driver_id')
        self.__main = await func.int_to_str(num=self.__data.get('wallet')[0])
        self.__bonus = await func.int_to_str(num=self.__data.get('wallet')[1])

    async def pay_way_form(self):
        await self._unpack_pay_way()
        form = Template("<b>$id</b>: $driver_id\n"
                        "<b>$cash</b>: $driver_cash $sum\n")
        form = form.substitute(id=self.__Lang.personal_cabinet.id, driver_id=self.__driver_id,
                               cash=self.__Lang.wallet.amount, sum=self.__Lang.symbol.sum,
                               driver_cash=self.__cash)
        return form

    async def _unpack_pay_way(self):
        self.__driver_id = self.__data.get('driver_id')
        self.__cash = await func.int_to_str(num=self.__data.get('cash'))

    async def payment_form(self):
        await self._unpack_payment()
        form = Template("$pay_way $type_payment\n"
                        "$amount: <b>$cash</b> $sum\n\n"
                        "<i>$payment</i>")
        form = form.substitute(pay_way=self.__Lang.wallet.pay_way2, type_payment=self.__type,
                               amount=self.__Lang.wallet.amount2, cash=self.__cash,
                               payment=self.__Lang.wallet.payment2, sum=self.__Lang.symbol.sum)
        return form

    async def _unpack_payment(self):
        self.__type = self.__data.get('type')
        self.__cash = await func.int_to_str(num=self.__data.get('cash'))

    async def payment_accept(self):
        form = Template("$accept <b>$cash</b> $sum")
        form = form.substitute(accept=self.__Lang.wallet.accept,  sum=self.__Lang.symbol.sum,
                               cash=await func.int_to_str(num=self.__data.get('cash')))
        return form
