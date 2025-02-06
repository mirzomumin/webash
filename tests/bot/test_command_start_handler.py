import pytest
from unittest.mock import AsyncMock, Mock

from aiogram import html
from aiogram.types import (
    Message,
    User,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from src.bot.app import command_start_handler


@pytest.mark.asyncio
async def test_command_start_handler():
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=User)
    mock_message.from_user.full_name = "Test User"
    mock_message.answer = AsyncMock()

    await command_start_handler(mock_message)

    contact_button = KeyboardButton(text="📞 Share your contact", request_contact=True)
    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[[contact_button]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    text = f"Hello, {html.bold(mock_message.from_user.full_name)}! \
        \n\rWelcome to @webash's official bot \
        \n\n\rPlease share your contact (by clicking button)"
    mock_message.answer.assert_called_once_with(text, reply_markup=contact_keyboard)
