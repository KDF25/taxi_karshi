from string import Template
from text.function.function import TextFunc
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()
func = TextFunc()


class FormOrderClient:
    def __init__(self, language: str, data: dict):
        self.__Lang: Model = Txt.language[language]
        self.__data = data

    async def menu_finally(self):
        text = Template('<b><s>$cashback: $cash_cashback $sum </s></b>\n'
                        '<b>$remainder</b>: $cash_remainder $sum\n\n'
                        '<b>$total — $cash_total $sum</b>')
        text = text.substitute(cashback=self.__Lang.start_driver.client.cashback2, sum=self.__Lang.symbol.sum,
                               cash_cashback=await self._cash(self.__data['lost_cashback']),
                               remainder=self.__Lang.start_driver.client.remainder,
                               cash_remainder=await self._cash(self.__data['pay']),
                               total=self.__Lang.start_driver.client.total,
                               cash_total=await self._cash(self.__data['pay']))
        return text

    async def menu_finally_driver(self):
        text = Template('$wallet <b>$cash_cashback $sum </b>\n'
                        '$pay <b>$cash_cashback $sum </b>\n\n'
                        '<b><s>$cashback: $cash_cashback $sum </s></b>\n'
                        '<b>$remainder</b>: $cash_remainder $sum\n\n'
                        '<b>$total — $cash_total $sum</b>')
        text = text.substitute(wallet=self.__Lang.start_driver.form.wallet, pay=self.__Lang.start_driver.form.pay,
                               cashback=self.__Lang.start_driver.client.cashback2, sum=self.__Lang.symbol.sum,
                               cash_cashback=await self._cash(self.__data['lost_cashback']),
                               remainder=self.__Lang.start_driver.client.remainder,
                               cash_remainder=await self._cash(self.__data['pay']),
                               total=self.__Lang.start_driver.client.total,
                               cash_total=await self._cash(self.__data['pay']))
        return text

    @staticmethod
    async def _cash(cash: int):
        return await func.int_to_str(num=cash)


