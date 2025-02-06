from datetime import datetime
from uuid import UUID

from aiogram.types.user import User as TelegramUser  # import telegram User schema
from pydantic import BaseModel, Field


class AddUserSchema(TelegramUser):
    # tid: int
    # first_name: str | None
    # last_name: str | None
    # username: str | None
    # is_bot: bool
    # language_code: str
    # is_premium: bool | None
    # added_to_attachment_menu: bool | None
    # can_join_groups: bool | None
    # can_read_all_group_messages: bool | None
    # supports_inline_queries: bool | None
    # can_connect_to_business: bool | None
    # has_main_web_app: bool | None

    @classmethod
    async def to_db(cls, telegram_user: TelegramUser):
        return {
            "tid": telegram_user.id,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "username": telegram_user.username,
            "is_bot": telegram_user.is_bot,
            "language_code": telegram_user.language_code,
            "is_premium": telegram_user.is_premium,
            "added_to_attachment_menu": telegram_user.added_to_attachment_menu,
            "can_join_groups": telegram_user.can_join_groups,
            "can_read_all_group_messages": telegram_user.can_read_all_group_messages,
            "supports_inline_queries": telegram_user.supports_inline_queries,
            "can_connect_to_business": telegram_user.can_connect_to_business,
            "has_main_web_app": telegram_user.has_main_web_app,
        }

    class ConfigDict:
        from_attributes = True


class UserSchema(BaseModel):
    id: UUID
    tid: int
    first_name: str | None
    last_name: str | None
    username: str | None
    is_bot: bool
    created_at: datetime


class GetUserSchema(BaseModel):
    user: UserSchema


class AccessToken(BaseModel):
    access: str


class RefreshToken(BaseModel):
    refresh: str


class Tokens(AccessToken, RefreshToken):
    pass


class TokensRsp(BaseModel):
    tokens: Tokens


class OtpData(BaseModel):
    otp_code: int = Field(..., ge=100_000, le=999_999)


class CustomTelegramUser(TelegramUser):
    phone_number: str

    @classmethod
    def to_db(cls, *, telegram_user: TelegramUser, phone_number: str):
        return {
            "tid": telegram_user.id,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "username": telegram_user.username,
            "phone_number": phone_number,
            "is_bot": telegram_user.is_bot,
            "language_code": telegram_user.language_code,
            "is_premium": telegram_user.is_premium,
            "added_to_attachment_menu": telegram_user.added_to_attachment_menu,
            "can_join_groups": telegram_user.can_join_groups,
            "can_read_all_group_messages": telegram_user.can_read_all_group_messages,
            "supports_inline_queries": telegram_user.supports_inline_queries,
            "can_connect_to_business": telegram_user.can_connect_to_business,
            "has_main_web_app": telegram_user.has_main_web_app,
        }

    class ConfigDict:
        from_attributes = True
