import pytest
from unittest.mock import AsyncMock, Mock, patch

from aiogram.types import Message, User as TelegramUser
from src.bot.app import command_login_handler
from src.core.models.user import Code, User
from src.core.repositories.user import UserRepository, CodeRepository
from tests.conftest import get_test_db


@pytest.mark.asyncio(loop_scope="session")
@patch("src.bot.service.get_db", get_test_db)
async def test_command_login_handler_success():
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=TelegramUser)
    mock_message.from_user.id = 12345
    mock_message.from_user.is_bot = False
    mock_message.from_user.first_name = "Anonym"
    mock_message.from_user.last_name = "Anonymous"
    mock_message.from_user.username = "anonymous"
    mock_message.from_user.language_code = "en"
    mock_message.from_user.is_premium = False
    mock_message.from_user.added_to_attachment_menu = False
    mock_message.from_user.can_join_groups = False
    mock_message.from_user.can_read_all_group_messages = True
    mock_message.from_user.supports_inline_queries = False
    mock_message.from_user.can_connect_to_business = False
    mock_message.from_user.has_main_web_app = False
    mock_message.answer = AsyncMock()

    await command_login_handler(mock_message)

    async with get_test_db() as db:
        user: User = await UserRepository.get(tid=mock_message.from_user.id, db=db)
        codes: list[Code] = await CodeRepository.list(
            filters=[Code.user_id == user.id], db=db
        )
        code = codes[-1]

    mock_message.answer.assert_called_once_with(f"🔐 Code: <code>{code.value}</code>")


@pytest.mark.asyncio(loop_scope="session")
@patch("src.bot.service.get_db", get_test_db)
async def test_command_login_handler_object_already_exists():
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=TelegramUser)
    mock_message.from_user.id = 12345
    mock_message.from_user.is_bot = False
    mock_message.from_user.first_name = "Anonym"
    mock_message.from_user.last_name = "Anonymous"
    mock_message.from_user.username = "anonymous"
    mock_message.from_user.language_code = "en"
    mock_message.from_user.is_premium = False
    mock_message.from_user.added_to_attachment_menu = False
    mock_message.from_user.can_join_groups = False
    mock_message.from_user.can_read_all_group_messages = True
    mock_message.from_user.supports_inline_queries = False
    mock_message.from_user.can_connect_to_business = False
    mock_message.from_user.has_main_web_app = False
    mock_message.answer = AsyncMock()

    await command_login_handler(mock_message)

    mock_message.answer.assert_called_once_with("Eski kodingiz hali ham kuchda ☝️")


@pytest.mark.asyncio
@patch("src.bot.service.BotService.get_auth_code")
async def test_command_login_handler_unexpected_error(mock_get_auth_code):
    mock_get_auth_code.side_effect = Exception("Unexpected error")
    mock_message = AsyncMock(spec=Message)
    mock_message.from_user = Mock(spec=TelegramUser)
    mock_message.from_user.id = 12345
    mock_message.answer = AsyncMock()

    await command_login_handler(mock_message)

    mock_get_auth_code.assert_awaited_once_with(user=mock_message.from_user)
    mock_message.answer.assert_called_once_with(
        "Birozdan so'ng qayta urinib ko'ring ⏳"
    )
