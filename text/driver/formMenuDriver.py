from math import ceil
from string import Template
from aiogram.utils.markdown import hlink

from text.function.function import TextFunc
from text.language.main import Text_main
from text.language.ru import Ru_language as Model
Txt = Text_main()
func = TextFunc()


class FormMenuDriver:
    def __init__(self, language: str, data: dict):
        self.__Lang: Model = Txt.language[language]
        self.__data = data

    async def menu_finish_driver(self):
        text = Template('$finish\n'
                        '<b>$onWay</b>: $cash_time $sum\n'
                        '<b>$paidWaiting</b>: $cash_waiting $sum\n'
                        '<b>$total — $cash_total $sum</b>\n\n'
                        '<i>$commission - $cash_commission $sum</i>')
        text = text.substitute(finish=self.__Lang.start_driver.form.finish,
                               onWay=self.__Lang.start_driver.form.onWay,
                               cash_time=await self._cash(self.__data['cash_time']), sum=self.__Lang.symbol.sum,
                               paidWaiting=self.__Lang.start_driver.form.paidWaiting,
                               cash_waiting=await self._cash(self.__data['cash_waiting']),
                               total=self.__Lang.start_driver.form.total,
                               cash_total=await self._cash(self.__data['cash_total']),
                               commission = self.__Lang.start_driver.form.commission,
                               cash_commission=await self._cash(self.__data['cash_commission']))
        return text

    async def menu_finish_client(self):
        text = Template('$finish\n'
                        '<b>$onWay</b>: $cash_time $sum\n'
                        '<b>$paidWaiting</b>: $cash_waiting $sum\n'
                        '<b>$total — $cash_total $sum</b>\n\n'
                        '<i>$cashbackNew — $new_cashback $sum</i>')
        text = text.substitute(finish=self.__Lang.start_driver.form.finish,
                               onWay=self.__Lang.start_driver.form.onWay,
                               cash_time=await self._cash(self.__data['cash_time']), sum=self.__Lang.symbol.sum,
                               paidWaiting=self.__Lang.start_driver.form.paidWaiting,
                               cash_waiting=await self._cash(self.__data['cash_waiting']),
                               total=self.__Lang.start_driver.form.total,
                               cash_total=await self._cash(self.__data['cash_total']),
                               cashbackNew=self.__Lang.start_driver.client.cashbackNew,
                               new_cashback=await self._cash(self.__data['new_cashback']))
        return text

    async def menu_pay_cashback(self):
        text = Template('<b>$cashback</b>: $cash $sum\n'
                        '<b>$pay</b>')
        text = text.substitute(cashback=self.__Lang.start_driver.client.cashback, sum=self.__Lang.symbol.sum,
                               cash=await self._cash(self.__data['cashback']), pay=self.__Lang.start_driver.client.pay)
        return text

    @staticmethod
    async def _cash(cash: int):
        return await func.int_to_str(num=cash)

    async def menu_onSpot_client(self):
        text = Template("$arrive\n"
                        "<b>🚙 $color $model — $number</b>\n\n"
                        "<b>$driver:</b> $driver_name\n"
                        "<b>$driver_phone:</b> $driver_phone2\n")
        text = text.substitute(arrive=self.__Lang.start_driver.client.arrive,
                               driver=self.__Lang.start_driver.client.driver, driver_name=self.__data['name'],
                               driver_phone=self.__Lang.start_driver.client.driver_phone,
                               driver_phone2=self.__data['phone_driver'],  color=self.__data['color'],
                               model=self.__data['model'], number=self.__data['number'])
        return text





