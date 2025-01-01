from aiogram.types.user import User  # import telegram User schema


class AddUserSchema(User):
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
    async def to_db(cls, data: User):
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
