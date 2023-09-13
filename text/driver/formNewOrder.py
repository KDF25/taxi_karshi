from string import Template

from aiogram.utils.markdown import hlink

from looping import pg
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class FormNewOrder:

    def __init__(self, language: str, data: dict = None):
        self.__language = language
        self.__Lang: Model = Txt.language[language]
        self.__data = data

    @staticmethod
    async def _comment(comment: str = None):
        if comment is None:
            return "..."
        else:
            return comment

    async def menu_accept_taxi(self):
        text = Template("$accept\n\n"
                        "<b>$client</b>\n\n"
                        "<b>$phone:</b> $phone_client\n"
                        "<b>$spot:</b> $spot_client\n"
                        "<b>$comment:</b> $comment_client\n\n"
                        "$location")
        text = text.substitute(accept=self.__Lang.new_order.accept.accept, client=self.__Lang.new_order.accept.client,
                               spot=self.__Lang.new_order.accept.spot,
                               spot_client=await pg.id_to_spot(id=self.__data['spot'], language=self.__language),
                               phone=self.__Lang.new_order.accept.phone,  phone_client=self.__data['phone_client'],
                               comment=self.__Lang.new_order.accept.comment,
                               comment_client=await self._comment(self.__data.get('comment')),
                               location=self.__Lang.new_order.accept.location)
        return text

    async def menu_accept_delivery_and_truck(self):
        text = Template("$accept\n\n"
                        "<b>$client</b>\n\n"
                        "<b>$phone:</b> $phone_client\n"
                        "<b>$comment:</b> $comment_client")
        text = text.substitute(accept=self.__Lang.new_order.accept.accept, client=self.__Lang.new_order.accept.client,
                               phone=self.__Lang.new_order.accept.phone,  phone_client=self.__data['phone_client'],
                               comment=self.__Lang.new_order.accept.comment,
                               comment_client=await self._comment(self.__data.get('comment')))
        return text

    async def menu_accept(self):
        text = Template("$accept "
                        "🚙<b>$color $model — $number</b>\n\n"
                        "<b>$driver:</b> $driver_name\n"
                        "<b>$phone:</b> $driver_phone\n"
                        "<i>$time</i>")
        text = text.substitute(accept=self.__Lang.new_order.client.accept,
                               color=self.__data['color'], model=self.__data['model'], number=self.__data['number'],
                               driver=self.__Lang.new_order.client.driver, driver_name=self.__data['name'],
                               phone=self.__Lang.new_order.client.phone, driver_phone=self.__data['phone_driver'],
                               time=self.__Lang.new_order.client.time)
        return text

    async def menu_accept_truck(self):
        text = Template("$accept "
                        "🚙<b>$model — $number</b>\n\n"
                        "<b>$driver:</b> $driver_name\n"
                        "<b>$phone:</b> $driver_phone\n"
                        "<i>$time</i>")
        text = text.substitute(accept=self.__Lang.new_order.client.accept, model=self.__data['model'],
                               number=self.__data['number'],
                               driver=self.__Lang.new_order.client.driver, driver_name=self.__data['name'],
                               phone=self.__Lang.new_order.client.phone, driver_phone=self.__data['phone_driver'],
                               time=self.__Lang.new_order.client.time)
        return text