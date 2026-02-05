"""ChatThread SQLModel for conversation persistence.

This module defines the ChatThread model representing a conversation session
between a user and the AI assistant.
"""

from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .chat_message import ChatMessage



class ChatThread(SQLModel, table=True):
    """Represents a conversation thread.

    A thread is a collection of messages exchanged between a user and the AI assistant.
    Threads are owned by users and cascade-deleted when the user is removed.

    Attributes:
        id: UUID primary key for global uniqueness
        user_id: Foreign key to user.id (owner of the thread)
        title: Optional conversation title
        created_at: Thread creation timestamp
        updated_at: Last message timestamp (updated on each message)
        messages: Relationship to ChatMessage (one-to-many)
    """

    __tablename__ = "chat_threads"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True
    )
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to ChatMessage
    messages: list["ChatMessage"] = Relationship(  # type: ignore
        back_populates="thread",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
