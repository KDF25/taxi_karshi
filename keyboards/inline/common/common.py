from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from text.language.main import Text_main
Txt = Text_main()


class Start:
    @staticmethod
    async def choose_language():
        markup = InlineKeyboardMarkup(row_width=3)
        b_rus = InlineKeyboardButton(text=Txt.settings.rus, callback_data='rus')
        b_ozb = InlineKeyboardButton(text=Txt.settings.uzb, callback_data='uzb')
        # b_uzb = InlineKeyboardButton(text=Txt.settings.ozb, callback_data='ozb')
        markup.row(b_ozb, b_rus)
        return markup
