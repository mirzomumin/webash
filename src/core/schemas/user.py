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
    async def to_db(cls, data: TelegramUser):
        return {
            "tid": data.id,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "username": data.username,
            "is_bot": data.is_bot,
            "language_code": data.language_code,
            "is_premium": data.is_premium,
            "added_to_attachment_menu": data.added_to_attachment_menu,
            "can_join_groups": data.can_join_groups,
            "can_read_all_group_messages": data.can_read_all_group_messages,
            "supports_inline_queries": data.supports_inline_queries,
            "can_connect_to_business": data.can_connect_to_business,
            "has_main_web_app": data.has_main_web_app,
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
    otp_code: int = Field(ge=100_000, le=999_999)
