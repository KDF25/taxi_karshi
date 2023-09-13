from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class InlineClient:
    def __init__(self, language: str = None, page: int = None, pages: int = None, order_id: int = None):
        self.__page = page
        self.__pages = pages
        self.__language = language
        self.__order_id = order_id
        self.__Lang: Model = Txt.language[self.__language]

    async def menu_tarif(self):
        markup = InlineKeyboardMarkup(row_width=3)
        b1 = InlineKeyboardButton(text="◀", callback_data="prev")
        b2 = InlineKeyboardButton(text=f"{self.__page} / {self.__pages}", callback_data="void")
        b3 = InlineKeyboardButton(text="▶", callback_data="next")
        markup.add(b1, b2, b3)
        return markup

    async def menu_accept_taxi(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.driver.accept2, callback_data=f"orderAcceptTaxi_{self.__order_id}")
        markup.add(b1)
        return markup

    async def menu_accept_delivery(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.driver.accept2, callback_data=f"orderAcceptDelivery_{self.__order_id}")
        markup.add(b1)
        return markup

    async def menu_accept_truck(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.driver.accept2, callback_data=f"orderAcceptTruck_{self.__order_id}")
        markup.add(b1)
        return markup

    async def menu_active_order(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.active_order.location, callback_data=f"location_{self.__order_id}")
        b2 = InlineKeyboardButton(text=self.__Lang.buttons.active_order.cancel, callback_data=f"cancel_{self.__order_id}")
        markup.add(b1, b2)
        return markup

    async def menu_location(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.active_order.location, callback_data=f"location_{self.__order_id}")
        markup.add(b1)
        return markup

    async def menu_delete_active_order(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.active_order.delete, callback_data=f"delete_{self.__order_id}")
        markup.add(b1)
        return markup

    async def menu_pay_cashback(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.client.taxi.cashbackPay, callback_data=f"cashbackPay_{self.__order_id}")
        # b2 = InlineKeyboardButton(text=self.__Lang.buttons.client.taxi.cashbackNotPay, callback_data=f"cashbackNotPay_{self.__order_id}")
        markup.add(b1)
        return markup

