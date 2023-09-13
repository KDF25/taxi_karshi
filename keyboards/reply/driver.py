from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class ReplyDriver:
    def __init__(self, language: str):
        self.__language = language
        self.Lang: Model = Txt.language[language]
        self.__main_menu = KeyboardButton(text=self.Lang.menu.client.menu)

    async def start_online(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.menu.driver.offline)
        b2 = KeyboardButton(text=self.Lang.menu.driver.wallet)
        b3 = KeyboardButton(text=self.Lang.menu.driver.settings)
        markup.add(b1, b2, b3)
        return markup

    async def start_offline(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.menu.driver.online)
        b2 = KeyboardButton(text=self.Lang.menu.driver.wallet)
        b3 = KeyboardButton(text=self.Lang.menu.driver.settings)
        markup.add(b1, b2, b3)
        return markup

    async def menu_settings(self):
        markup = ReplyKeyboardMarkup(row_width=3)
        b1 = KeyboardButton(text=self.Lang.information.personalData)
        b2 = KeyboardButton(text=self.Lang.information.about_us)
        b3 = KeyboardButton(text=self.Lang.information.language)
        b4 = KeyboardButton(text=self.Lang.information.feedback)
        markup.add(b1).add(b2, b3, b4).add(self.__main_menu)
        return markup

    async def menu_language(self):
        markup = ReplyKeyboardMarkup(row_width=3)
        # b1 = KeyboardButton(text=Txt.settings.ozb)
        b2 = KeyboardButton(text=Txt.settings.rus)
        b3 = KeyboardButton(text=Txt.settings.uzb)
        markup.add(b2, b3).add(self.__main_menu)
        return markup

    async def menu_phone(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.menu.client.myPhone, request_contact=True)
        markup.add(b1)
        return markup

    async def main_menu(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        markup.add(self.__main_menu)
        return markup

    async def menu_on_spot(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.menu.driver.onSpot, request_location=True)
        b2 = KeyboardButton(text=self.Lang.menu.driver.orderData)
        markup.add(b1, b2)
        return markup

    async def menu_start_trip(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.start)
        b2 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.orderData)
        markup.add(b1, b2)
        return markup

    async def menu_finish_trip(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.finish, request_location=True)
        b2 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.waiting)
        b3 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.orderData)
        markup.add(b1, b2, b3)
        return markup

    async def menu_waiting_trip(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.finish, request_location=True)
        b2 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.letsGo)
        b3 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.orderData)
        markup.add(b1, b2, b3)
        return markup

    async def menu_finish_trip2(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        b1 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.finish, request_location=True)
        b3 = KeyboardButton(text=self.Lang.buttons.driver.onSpot.orderData)
        markup.add(b1, b3)
        return markup






