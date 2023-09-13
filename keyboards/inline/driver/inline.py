

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from looping import pg
from text.language.main import Text_main
from text.function.function import TextFunc
from text.language.ru import Ru_language as Model
Txt = Text_main()
func = TextFunc()


class InlineDriverData:
    def __init__(self, language: str, spots: list = None, delivery: bool = False, truck: bool = False,
                 pay_id: int = None, car_type: str = None, car_subtype: str = None, order_id: int = None):
        self.__markup = None
        self.__language = language
        self.__spots = spots
        self.__delivery = delivery
        self.__truck = truck
        self.__pay_id = pay_id
        self.__order_id = order_id
        self.__car_type = car_type
        self.__car_subtype = car_subtype
        self.__Lang: Model = Txt.language[language]
        self.__back = InlineKeyboardButton(text=self.__Lang.buttons.driver.back, callback_data="back")

    async def menu_auto(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.personal_cabinet.model, callback_data=f"model")
        b2 = InlineKeyboardButton(text=self.__Lang.buttons.personal_cabinet.number, callback_data=f"number")
        b3 = InlineKeyboardButton(text=self.__Lang.buttons.personal_cabinet.color, callback_data=f"colors")
        markup.add(b1, b2, b3, self.__back)
        return markup

    async def menu_taxi(self):
        self.__markup = InlineKeyboardMarkup(row_width=3)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.personal_cabinet.truck, callback_data=f"truck")
        self.__markup.add(b1)
        await self._taxi()
        self.__markup.add(self.__back)
        return self.__markup

    async def _taxi(self):
        cars = await pg.id_and_model(car_type="taxi")
        for index, car in enumerate(cars):
            b = InlineKeyboardButton(text=car[1], callback_data=f"car_{car[0]}")
            if index == 0:
                self.__markup.add(b)
            else:
                self.__markup.insert(b)

    async def menu_car_subtype(self):
        self.__markup = InlineKeyboardMarkup(row_width=1)
        await self._car_subtype()
        self.__markup.add(self.__back)
        return self.__markup

    async def _car_subtype(self):
        elements = await pg.id_and_car_subtype(car_type="truck", language=self.__language)
        for element in elements:
            b = InlineKeyboardButton(text=element[1], callback_data=f"subtype_{element[0]}")
            self.__markup.insert(b)

    async def menu_trucks(self):
        self.__markup = InlineKeyboardMarkup(row_width=3)
        await self._trucks()
        self.__markup.add(self.__back)
        return self.__markup

    async def _trucks(self):
        print(self.__car_type, self.__car_subtype)
        cars = await pg.id_and_model2(car_type=self.__car_type, car_subtype=self.__car_subtype)
        for index, car in enumerate(cars):
            b = InlineKeyboardButton(text=car[1], callback_data=f"truck_{car[0]}")
            self.__markup.insert(b)

    async def menu_color(self):
        self.__markup = InlineKeyboardMarkup(row_width=3)
        await self._color()
        self.__markup.add(self.__back)
        return self.__markup

    async def _color(self):
        colors = await pg.id_and_color(language=self.__language)
        for color in colors:
            b = InlineKeyboardButton(text=color[1], callback_data=f"color_{color[0]}")
            self.__markup.insert(b)

    async def menu_back(self):
        self.__markup = InlineKeyboardMarkup(row_width=1)
        self.__markup.add(self.__back)
        return self.__markup

    async def menu_agreement(self):
        self.__markup = InlineKeyboardMarkup(row_width=2)
        b_no = InlineKeyboardButton(text=self.__Lang.buttons.driver.no, callback_data='back')
        b_yes = InlineKeyboardButton(text=self.__Lang.buttons.driver.yes, callback_data='agree')
        self.__markup.add(b_no, b_yes, self.__back)
        return self.__markup

    async def menu_personal_data(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.personal_cabinet.name, callback_data=f"name")
        b2 = InlineKeyboardButton(text=self.__Lang.buttons.personal_cabinet.phone, callback_data=f"phone")
        b3 = InlineKeyboardButton(text=self.__Lang.buttons.personal_cabinet.car, callback_data=f"auto")
        markup.add(b1, b2, b3)
        return markup

    async def menu_spots(self):
        self.__markup = InlineKeyboardMarkup(row_width=3)
        # await self._delivery()
        await self._spots()
        accept = InlineKeyboardButton(text=self.__Lang.buttons.driver.accept, callback_data="accept")
        self.__markup.add(accept)
        return self.__markup

    async def _delivery(self):
        text = self.__Lang.buttons.driver.delivery
        text = text if self.__delivery is False else "✅" + text
        b = InlineKeyboardButton(text=text, callback_data=f"delivery")
        self.__markup.insert(b)

    async def _truck(self):
        text = self.__Lang.buttons.driver.truck
        text = text if self.__truck is False else "✅" + text
        b = InlineKeyboardButton(text=text, callback_data=f"truck")
        self.__markup.insert(b)

    async def _spots(self):
        button_list = [1, 15, 17, 19, 24, 29]
        spots = await pg.id_and_spot(language=self.__language)
        # i = 1
        for index, spot in enumerate(spots):

            b = InlineKeyboardButton(text=await self._check_spot(spot), callback_data=f"spot_{spot[0]}")

            if index == 0:
                self.__markup.add(b)
                await self._delivery()
                await self._truck()

            elif index in button_list:

                self.__markup.add(b)
            else:
                self.__markup.insert(b)
            # i += 1
            #
            # i = 1 if i == 4 else i
            # i = 2 if i == 5 else i


    async def _check_spot(self, spot: list):
        if spot[0] in self.__spots:
            return "✅" + spot[1]
        else:
            return spot[1]

    async def menu_accept(self):
        markup = InlineKeyboardMarkup(row_width=1)
        accept = InlineKeyboardButton(text=self.__Lang.buttons.driver.accept, callback_data=f"paymentAccept_{self.__pay_id}")
        reject = InlineKeyboardButton(text=self.__Lang.buttons.driver.reject, callback_data=f"paymentReject_{self.__pay_id}")
        markup.add(accept, reject)
        return markup

    async def menu_cancel_active_order(self):
        Lang: Model = Txt.language[self.__language]
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=Lang.buttons.active_order.cancel, callback_data=f"cancel_{self.__order_id}")
        markup.add(b1)
        return markup

    async def menu_delete_active_order(self):
        Lang: Model = Txt.language[self.__language]
        markup = InlineKeyboardMarkup(row_width=1)
        b1 = InlineKeyboardButton(text=Lang.buttons.active_order.delete, callback_data=f"delete_{self.__order_id}")
        markup.add(b1)
        return markup

    async def menu_balance(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b = InlineKeyboardButton(text=self.__Lang.buttons.wallet.balance, callback_data="balance")
        markup.add(b)
        return markup

    async def menu_cash(self):
        self.__markup = InlineKeyboardMarkup(row_width=2)
        await self._cash()
        self.__markup.add(self.__back)
        return self.__markup

    async def _cash(self):
        for cash in Txt.money.wallet.price:
            text = await func.int_to_str(num=cash)
            b = InlineKeyboardButton(text=text, callback_data=f"cash_{cash}")
            self.__markup.insert(b)

    async def menu_pay_way(self):
        markup = InlineKeyboardMarkup(row_width=3)
        b1 = InlineKeyboardButton(text=self.__Lang.buttons.wallet.payme, callback_data="Payme")
        b2 = InlineKeyboardButton(text=self.__Lang.buttons.wallet.click, callback_data="Click")
        b3 = InlineKeyboardButton(text=self.__Lang.buttons.wallet.paynet, callback_data="Paynet")
        markup.add(b1, b2, b3).add(self.__back)
        return markup

    async def menu_payment(self):
        markup = InlineKeyboardMarkup(row_width=1)
        b = InlineKeyboardButton(text=self.__Lang.buttons.wallet.pay, callback_data="pay")
        markup.add(b, self.__back)
        return markup

    async def payme_url(self):
        markup = InlineKeyboardMarkup(row_width=1)
        url_button = InlineKeyboardButton(text=self.__Lang.buttons.wallet.pay, callback_data="payed")
        markup.add(url_button, self.__back)
        return markup

    async def click_url(self):
        markup = InlineKeyboardMarkup(row_width=1)
        url_button = InlineKeyboardButton(text=self.__Lang.buttons.wallet.pay,  callback_data="payed")
        markup.add(url_button, self.__back)
        return markup
