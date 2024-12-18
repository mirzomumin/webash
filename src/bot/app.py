import asyncio
import logging
import sys

# Добавляем корневую директорию в sys.path
# sys.path.append(os.path.dirname(os.path.abspath(os.path.join(__file__, "../.."))))

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.command import CommandLogin
from src.config import settings
from src.users.repository import UserRepository
from src.users.service import AddUserSchema
from src.utils import get_random_number
from src.database import get_db


# Bot token can be obtained via https://t.me/BotFather
TOKEN = settings.BOT_TOKEN

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(CommandLogin())
async def command_login_handler(message: Message) -> None:
    """
    This handler receives messages with `/login` command.
    Send otp code in return.
    """
    rand_num = get_random_number()
    async with get_db() as db:
        user_data = await AddUserSchema.to_db(message.from_user)
        user = await UserRepository.get(db=db, tid=user_data["tid"])
        if user is None:
            user = await UserRepository.add(db=db, values=user_data)
            await db.commit()
            await db.refresh(user)
    await message.answer(f"🔐 Code: {html.code(rand_num)}")


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
