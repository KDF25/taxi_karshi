from string import Template

from looping import pg
from text.language.main import Text_main
from text.language.ru import Ru_language as Model
Txt = Text_main()


class FormPersonalData:

    def __init__(self, data=None):
        self.__data = data
        self.__language = self.__data.get('lang')
        self.__Lang: Model = Txt.language[self.__data.get('lang')]

    async def personal_data_form(self):
        await self._unpack_data()
        text = Template("<b>$id</b>: $driver_id\n"
                        "<b>$name</b>: $driver_name\n"
                        "<b>$phone</b>: $driver_phone\n"
                        "<b>$car</b>: $color $driver_car — $number\n")
        text = text.substitute(id=self.__Lang.personal_cabinet.id, driver_id=self.__driver_id,
                               name=self.__Lang.personal_cabinet.name, driver_name=self.__name,
                               phone=self.__Lang.personal_cabinet.phone, driver_phone=self.__phone_driver,
                               car=self.__Lang.personal_cabinet.car, driver_car=self.__car, color=self.__color,
                               number=self.__number)
        return text

    async def _unpack_data(self):
        self.__driver_id = self.__data.get('driver_id')
        self.__name = self.__data.get('name')
        self.__phone_driver = self.__data.get('phone_driver')
        self.__number = self.__data.get('number')
        self.__car = self.__data.get('model')
        self.__color = self.__data.get('color')

    async def change_car(self):
        await self._unpack_data()
        text = Template("<b>$car</b>: $color $driver_car — $number\n\n"
                        "$new_data")
        text = text.substitute(car=self.__Lang.personal_cabinet.car, driver_car=self.__car, color=self.__color,
                               new_data=self.__Lang.personal_cabinet.new_data, number=self.__number)
        return text

    async def change_number(self):
        await self._unpack_data()
        text = Template("<b>$car</b>: $color $driver_car — $number\n\n"
                        "$sample\n\n")
        text = text.substitute(car=self.__Lang.personal_cabinet.car, driver_car=self.__car, color=self.__color,
                               sample=self.__Lang.registration.number, number=self.__number)
        return text

    async def _unpack_driver(self):
        self.__car = self.__data.get('car')
        self.__color = self.__data.get('color')
        self.__number = self.__data.get('number')
