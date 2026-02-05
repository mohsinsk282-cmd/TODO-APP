"""ChatMessage SQLModel for message persistence.

This module defines the ChatMessage model representing individual messages
within a conversation thread.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import CheckConstraint

if TYPE_CHECKING:
    from .chat_thread import ChatThread



class ChatMessage(SQLModel, table=True):
    """Represents a single message in a conversation thread.

    Messages are immutable after creation and belong to a specific thread.
    Role is constrained to 'user', 'assistant', or 'system'.

    Attributes:
        id: Auto-incrementing BIGSERIAL primary key
        thread_id: Foreign key to chat_threads.id
        role: Message sender role (user|assistant|system)
        content: Message text content
        created_at: Message creation timestamp
        thread: Relationship to ChatThread (many-to-one)
    """

    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="check_role"
        ),
    )

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )  # Auto-increment
    thread_id: str = Field(
        foreign_key="chat_threads.id",
        index=True
    )
    role: str  # Enum enforced by CHECK constraint
    content: str
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True
    )

    # Relationship to ChatThread
    thread: "ChatThread" = Relationship(  # type: ignore
        back_populates="messages"
    )
