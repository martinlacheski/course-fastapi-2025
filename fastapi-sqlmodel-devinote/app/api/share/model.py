from datetime import datetime
from enum import Enum

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class ShareRole(str, Enum):
    READ = "read"
    EDIT = "edit"
    DELETE = "delete"


class NoteShare(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("note_id", "user_id", name="uq_note_user"),
    )

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    note_id: int = Field(foreign_key="note.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: ShareRole = Field(default=ShareRole.READ)


class LabelShare(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("label_id", "user_id", name="uq_label_user"),
    )

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    label_id: int = Field(foreign_key="label.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: ShareRole = Field(default=ShareRole.READ)


class ShareRequest(SQLModel):
    target_user_id: int = Field(gt=0)
    role: ShareRole = ShareRole.READ
