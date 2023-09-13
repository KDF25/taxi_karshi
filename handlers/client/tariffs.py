from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound

from dispatcher import bot_client as bot
from keyboards.inline.client.inline import InlineClient
from text.language.main import Text_main
from text.language.ru import Ru_language as Model

Txt = Text_main()


class TariffsClient(StatesGroup):
    tariffs_level1 = State()

    async def menu_tariffs(self, message: types.Message, state: FSMContext):
        await self.tariffs_level1.set()
        async with state.proxy() as data:
            Lang: Model = Txt.language[data.get('lang')]
            data['page'] = 1
            data['pages'] = len(Lang.tarif.client.tarif_dict)
            Lang, inline = await self._prepare(data)
            inline = InlineClient(page=data['page'], language=data.get('lang'), pages=data['pages'])
        await bot.send_message(chat_id=message.from_user.id, text=Lang.tarif.client.tarif_dict[data['page']], reply_markup=await inline.menu_tarif())

    @staticmethod
    async def _prepare(data: dict):
        Lang: Model = Txt.language[data.get('lang')]
        inline = InlineClient(pages=data['pages'], page=data['page'], language=data.get('lang'))
        return Lang, inline

    async def menu_change_tariffs(self, call: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['page'] = await self._change_tariffs(page=data['page'], type_=call.data, pages=data['pages'])
            Lang, inline = await self._prepare(data)
        with suppress(MessageNotModified, MessageToEditNotFound):
            await call.answer()
            await bot.edit_message_text(chat_id=call.from_user.id, text=Lang.tarif.client.tarif_dict[data['page']],
                                        reply_markup=await inline.menu_tarif(), message_id=call.message.message_id)

    @staticmethod
    async def _change_tariffs(page: int, pages: int, type_: str):
        if pages > page >= 1 and type_ == "next":
            return page + 1
        elif pages >= page > 1 and type_ == "prev":
            return page - 1
        else:
            return page

    def register_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.menu_tariffs, text=Txt.client.menu.tarif,                                      state="*")
        dp.register_callback_query_handler(self.menu_change_tariffs, text=["prev", "next"],                             state=self.tariffs_level1)


