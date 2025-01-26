from uuid import UUID
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base.models import Base


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

    # relatioinship
    codes: Mapped[list["Code"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.tid


class Code(Base):
    __tablename__ = "codes"

    value: Mapped[int]
    expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_used: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # relatioinship
    user: Mapped[User] = relationship(back_populates="codes")
