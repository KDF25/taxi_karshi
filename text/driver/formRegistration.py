from string import Template
from aiogram.utils.markdown import hlink

from looping import pg
from text.language.main import Text_main
from text.language.ru import Ru_language as Model
Txt = Text_main()


class FormRegistration:
    def __init__(self, data=None):
        self.__data = data
        self.__Lang: Model = Txt.language[self.__data.get('lang')]

    async def agreement_car(self):
        await self._unpack_driver()
        color = await pg.id_to_color(self.__data.get('color'), self.__data.get('lang'))
        text = Template("<b>$name</b>: $driver_name\n"
                        "<b>$phone</b>: +$driver_phone\n"
                        "<b>$car</b>: $color $driver_car — $car_number\n\n"
                        "$question $about_us")
        text = text.substitute(name=self.__Lang.personal_cabinet.name, driver_name=self.__data.get('name'),
                               phone=self.__Lang.personal_cabinet.phone, driver_phone=self.__data.get('phone'),
                               car=self.__Lang.personal_cabinet.car, driver_car=self.__car, color=color,
                               car_number=self.__number, question=self.__Lang.registration.agreement,
                               about_us=await self.menu_about_us())
        return text

    async def agreement_truck(self):
        await self._unpack_driver()
        text = Template("<b>$name</b>: $driver_name\n"
                        "<b>$phone</b>: +$driver_phone\n"
                        "<b>$car</b>: $driver_car — $car_number\n\n"
                        "$question $about_us")
        text = text.substitute(name=self.__Lang.personal_cabinet.name, driver_name=self.__data.get('name'),
                               phone=self.__Lang.personal_cabinet.phone, driver_phone=self.__data.get('phone'),
                               car=self.__Lang.personal_cabinet.car, driver_car=self.__car,
                               car_number=self.__number, question=self.__Lang.registration.agreement,
                               about_us=await self.menu_about_us())
        return text

    async def _unpack_driver(self):
        self.__car = (await pg.id_to_model(self.__data.get('car')))[0]
        self.__number = self.__data.get('number')


    async def finish(self):
        form = Template("<b>$id</b>: $driver_id\n"
                        "$congratulation\n\n"
                        "$about_us\n\n"
                        "$online")
        form = form.substitute(id=self.__Lang.personal_cabinet.id, driver_id=self.__data.get('user_id'),
                               congratulation=self.__Lang.personal_cabinet.congratulation,
                               about_us=await self.menu_about_us(), online=self.__Lang.personal_cabinet.online)
        return form

    async def menu_about_us(self):
        text = Template('$text1')
        text = text.substitute(text1=hlink(url=self.__Lang.url.driver.about_us,
                                           title=self.__Lang.about_us.about_us))
        return text
