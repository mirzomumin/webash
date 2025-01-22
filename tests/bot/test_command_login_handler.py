import pytest
from unittest.mock import AsyncMock, Mock, patch

from aiogram.types import Message, User
from src.bot.app import command_login_handler
from src.core.utils.exceptions import ObjectAlreadyExists


@pytest.mark.asyncio
@patch("src.bot.service.BotService.get_auth_code")
async def test_command_login_handler_success(mock_get_auth_code):
    mock_get_auth_code.return_value = "123456"
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=User)
    mock_message.from_user.id = 12345
    mock_message.answer = AsyncMock()

    await command_login_handler(mock_message)

    mock_get_auth_code.assert_awaited_once_with(user=mock_message.from_user)
    mock_message.answer.assert_called_once_with("🔐 Code: <code>123456</code>")


@pytest.mark.asyncio
@patch("src.bot.service.BotService.get_auth_code")
async def test_command_login_handler_object_already_exists(mock_get_auth_code):
    mock_get_auth_code.side_effect = ObjectAlreadyExists
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=User)
    mock_message.from_user.id = 12345
    mock_message.answer = AsyncMock()

    await command_login_handler(mock_message)

    mock_get_auth_code.assert_awaited_once_with(user=mock_message.from_user)
    mock_message.answer.assert_called_once_with("Eski kodingiz hali ham kuchda ☝️")


@pytest.mark.asyncio
@patch("src.bot.service.BotService.get_auth_code")
async def test_command_login_handler_unexpected_error(mock_get_auth_code):
    mock_get_auth_code.side_effect = Exception("Unexpected error")
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=User)
    mock_message.from_user.id = 12345
    mock_message.answer = AsyncMock()

    await command_login_handler(mock_message)

    mock_get_auth_code.assert_awaited_once_with(user=mock_message.from_user)
    mock_message.answer.assert_called_once_with(
        "Birozdan so'ng qayta urinib ko'ring ⏳"
    )
