import phonenumbers
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from phonenumbers.phonenumberutil import NumberParseException

from dispatcher import bot_driver as bot
from looping import pg
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class IsNumber(BoundFilter):
    async def check(self, message: types.Message):
        lang = await pg.select_language_driver(user_id=message.from_user.id)
        Text_lang: Model = Txt.language[lang]
        number = message.text
        if number[0:2].isnumeric() and (len(number) == 8 or len(number) == 9):
            if len(number) == 8 and number[2:5].isnumeric() and number[6:].isalpha():
                return True
            elif len(number) == 8 and number[3:6].isnumeric() and number[7:].isalpha() and number[2].isalpha():
                return True
            elif len(number) == 9 and number[2].isalpha() and number[4:].isnumeric():
                return True
            else:
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.driver.nonFormat)
        else:
            await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.driver.nonFormat)


class IsPhone(BoundFilter):
    async def check(self, message: types.Message):
        lang = await pg.select_language_driver(user_id=message.from_user.id)
        Text_lang: Model = Txt.language[lang]
        try:
            my_string_number = "+" + str(int(message.text))
            my_number = phonenumbers.parse(my_string_number)
            if phonenumbers.is_valid_number(my_number) is True and message.text.replace("+", "").isnumeric():
                return True
            else:
                await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.driver.nonFormat)
        except Exception:
            await bot.send_message(chat_id=message.from_user.id, text=Text_lang.alert.driver.nonFormat)

