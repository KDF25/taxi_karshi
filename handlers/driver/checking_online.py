from keyboards.reply.driver import ReplyDriver
from looping import pg


async def checking_online(user_id: int, language: str):
    reply = ReplyDriver(language=language)
    condition = await pg.select_status_driver(driver_id=user_id)
    return await reply.start_online() if condition else await reply.start_offline()
