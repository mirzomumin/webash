from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class User(Base):
    __tablename__ = "users"

    tid: Mapped[int] = mapped_column(unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    username: Mapped[str | None] = mapped_column(
        String(200), unique=True, nullable=True
    )
    is_bot: Mapped[bool]
    language_code: Mapped[str] = mapped_column(String(2))
    is_premium: Mapped[bool | None]
    added_to_attachment_menu: Mapped[bool | None]
    can_join_groups: Mapped[bool | None]
    can_read_all_group_messages: Mapped[bool | None]
    supports_inline_queries: Mapped[bool | None]
    can_connect_to_business: Mapped[bool | None]
    has_main_web_app: Mapped[bool | None]

    def __str__(self) -> str:
        return self.tid
