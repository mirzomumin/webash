import pytest
from unittest.mock import AsyncMock, Mock

from aiogram.types import Message, User
from src.bot.app import command_start_handler


@pytest.mark.asyncio
async def test_command_start_handler():
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=User)
    mock_message.from_user.full_name = "Test User"
    mock_message.answer = AsyncMock()

    await command_start_handler(mock_message)

    mock_message.answer.assert_called_once_with("Hello, <b>Test User</b>!")
