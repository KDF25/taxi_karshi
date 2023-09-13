from string import Template

from looping import pg
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class FormPassenger:

    def __init__(self, language: str = None, data: dict = None):
        self.__language = language if language is not None else data['lang']
        self.__Lang: Model = Txt.language[self.__language] 
        self.__data = data

    async def _comment(self):
        if self.__data.get('comment') is None:
            return "..."
        else:
            return self.__data.get('comment')

    async def menu_location(self) -> str:
        text = Template("$taxi — $type\n\n"
                        "$location")
        text = text.substitute(taxi=self.__Lang.client.form.taxi, type=await self._type(),
                               location=self.__Lang.client.location)
        return text

    async def menu_start(self) -> str:
        text = Template("<b>$cashback: $cash $sum</b>\n"
                        "$cashback2\n\n"
                        "$text")
        text = text.substitute(cashback=self.__Lang.client.cashback,
                               cash=self.__data["cashback"],
                               sum=self.__Lang.symbol.sum,
                               cashback2=self.__Lang.client.cashback2,
                               text=self.__Lang.client.choose)
        return text

    async def _type(self) -> str:
        return (await pg.id_to_car_subtype(car_subtype=self.__data['type'], language=self.__language))[0]

    async def menu_find(self) -> str:
        text = Template("$find\n\n"
                        "$taxi — $type\n"
                        "<b>$phone:</b> +$phone_client\n"
                        "<b>$comment:</b> $comment_client")
        text = text.substitute(find=self.__Lang.client.find, 
                               taxi=self.__Lang.client.form.taxi, type=await self._type(),
                               phone=self.__Lang.client.form.phone, phone_client=int(self.__data['phone']),
                               comment=self.__Lang.client.form.comment, comment_client=await self._comment())
        return text

    async def menu_phone(self) -> str:
        text = Template("<b>$phone:</b> $phone_client\n\n"
                        "$share_phone")
        text = text.substitute(phone=self.__Lang.phone.client.number, phone_client=self.__data.get('phone', '...'),
                               share_phone=self.__Lang.phone.client.share_phone)
        return text

    async def menu_mailing(self) -> str:
        text = Template("<b>$new_order</b>\n\n"
                        "$taxi — $type\n\n"
                        "<b>$spot:</b> $spot_client\n"
                        "<b>$comment:</b> $comment_client\n\n"
                        "$order")
        text = text.substitute(new_order=self.__Lang.new_order.new_order.new_order,
                               taxi=self.__Lang.new_order.new_order.taxi, type=await self._type(),
                               spot=self.__Lang.new_order.new_order.spot,
                               spot_client=await pg.id_to_spot(id=self.__data['spot'], language=self.__language),
                               comment=self.__Lang.new_order.new_order.comment,
                               comment_client=await self._comment(),
                               order=self.__Lang.new_order.new_order.order)
        return text

    async def menu_active_order(self) -> str:
        text = Template("$taxi — $type\n"
                        "<b>$status:</b> $status_client\n"
                        "<b>$client_phone:</b> $client_phone2\n"
                        "<b>$comment:</b> $client_comment")
        text = text.substitute(taxi=self.__Lang.client.form.taxi, type=await self._type(),
                               status=self.__Lang.active_order.status, status_client=self.__Lang.active_order.waiting,
                               client_phone=self.__Lang.active_order.client_phone,
                               client_phone2=self.__data['client_phone'],
                               comment=self.__Lang.active_order.comment,
                               client_comment=await self._comment())
        return text

    async def menu_active_order_accepted(self) -> str:
        text = Template("$taxi — $type\n"
                        "<b>$status:</b> $status_client\n"
                        "<b>$client_phone:</b> $client_phone2\n"
                        "<b>$comment:</b> $client_comment\n\n"
                        "<b>$driver:</b> $driver_name\n"
                        "<b>$driver_phone:</b> $driver_phone2\n"
                        "<b>🚙 $color $model — $number</b>")
        text = text.substitute(taxi=self.__Lang.client.form.taxi, type=await self._type(),
                               status=self.__Lang.active_order.status, status_client=self.__Lang.active_order.accept,
                               client_phone=self.__Lang.active_order.client_phone,
                               client_phone2=self.__data['client_phone'],
                               comment=self.__Lang.active_order.comment,
                               client_comment=await self._comment(),
                               driver=self.__Lang.active_order.driver, driver_name=self.__data['name'],
                               driver_phone=self.__Lang.active_order.driver_phone,
                               driver_phone2=self.__data['driver_phone'], color=self.__data['color'],
                               model=self.__data['model'], number=self.__data['number'])
        return text
