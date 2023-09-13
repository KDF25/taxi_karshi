from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class ReplyClient:
    def __init__(self, language: str):
        self.__language = language
        self.Lang: Model = Txt.language[language]
        self.__main_menu = KeyboardButton(text=self.Lang.menu.client.menu)

    async def start(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = KeyboardButton(text=self.Lang.menu.client.taxi)
        b2 = KeyboardButton(text=self.Lang.menu.client.delivery)
        b3 = KeyboardButton(text=self.Lang.menu.client.truck)
        b4 = KeyboardButton(text=self.Lang.menu.client.order)
        b5 = KeyboardButton(text=self.Lang.menu.client.phone)
        b6 = KeyboardButton(text=self.Lang.menu.client.tarif)
        b7 = KeyboardButton(text=self.Lang.menu.client.lang)
        b8 = KeyboardButton(text=self.Lang.menu.client.change)
        markup.add(b1).add(b2, b3).add(b4, b5).add(b6, b7).add(b8)
        return markup

    async def menu_phone(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = KeyboardButton(text=self.Lang.menu.client.myPhone, request_contact=True)
        b2 = KeyboardButton(text=self.Lang.menu.client.menu)
        markup.add(b1, b2)
        return markup

    async def menu_language(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        # b1 = KeyboardButton(text=Txt.settings.ozb)
        b2 = KeyboardButton(text=Txt.settings.rus)
        b3 = KeyboardButton(text=Txt.settings.uzb)
        markup.add(b2, b3).add(self.__main_menu)
        return markup

    async def menu_taxi(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b1 = KeyboardButton(text=self.Lang.buttons.client.taxi.standard)
        b2 = KeyboardButton(text=self.Lang.buttons.client.taxi.comfort)
        markup.add(b1, b2).add(self.__main_menu)
        return markup

    async def menu_truck(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = KeyboardButton(text=self.Lang.buttons.client.truck.small)
        b2 = KeyboardButton(text=self.Lang.buttons.client.truck.medium)
        b3 = KeyboardButton(text=self.Lang.buttons.client.truck.big)
        markup.add(b1, b2, b3).add(self.__main_menu)
        return markup

    async def menu_location(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = KeyboardButton(text=self.Lang.buttons.client.taxi.location, request_location=True)
        markup.add(b1, self.__main_menu)
        return markup

    async def menu_comment(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        b1 = KeyboardButton(text=self.Lang.buttons.client.taxi.comment)
        markup.add(b1, self.__main_menu)
        return markup

    async def main_menu(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(self.__main_menu)
        return markup
