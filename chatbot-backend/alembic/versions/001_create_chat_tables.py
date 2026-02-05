"""Create chat_threads and chat_messages tables

Revision ID: 001
Revises:
Create Date: 2026-02-04

This migration creates the database schema for persistent chat history:
- chat_threads: Stores conversation threads with user ownership
- chat_messages: Stores individual messages within threads

Tables support:
- User isolation (user_id foreign key and indexes)
- Message ordering (created_at index)
- CASCADE DELETE (threads/messages removed when user deleted)
- Role validation (CHECK constraint for user/assistant/system)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chat_threads and chat_messages tables with proper constraints and indexes."""

    # Create chat_threads table
    op.create_table(
        'chat_threads',
        sa.Column('id', sa.String(), nullable=False, comment='UUID v4 primary key'),
        sa.Column('user_id', sa.String(), nullable=False, comment='Owner user ID from Better Auth'),
        sa.Column('title', sa.String(), nullable=True, comment='Optional thread title'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Thread creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Last message timestamp'),
        sa.PrimaryKeyConstraint('id', name='pk_chat_threads'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
            name='fk_chat_threads_user_id',
            ondelete='CASCADE'  # Delete threads when user is deleted
        ),
        comment='Conversation threads for chat history'
    )

    # Create index on user_id for efficient user filtering
    op.create_index(
        'ix_chat_threads_user_id',
        'chat_threads',
        ['user_id']
    )

    # Create index on updated_at for ordering threads
    op.create_index(
        'ix_chat_threads_updated_at',
        'chat_threads',
        ['updated_at'],
        postgresql_using='btree'
    )

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True, comment='Auto-incrementing message ID'),
        sa.Column('thread_id', sa.String(), nullable=False, comment='Parent thread UUID'),
        sa.Column('role', sa.String(), nullable=False, comment='Message role: user, assistant, or system'),
        sa.Column('content', sa.Text(), nullable=False, comment='Message text content'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Message creation timestamp'),
        sa.PrimaryKeyConstraint('id', name='pk_chat_messages'),
        sa.ForeignKeyConstraint(
            ['thread_id'],
            ['chat_threads.id'],
            name='fk_chat_messages_thread_id',
            ondelete='CASCADE'  # Delete messages when thread is deleted
        ),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name='ck_chat_messages_role'
        ),
        comment='Individual messages within conversation threads'
    )

    # Create index on thread_id for efficient thread message queries
    op.create_index(
        'ix_chat_messages_thread_id',
        'chat_messages',
        ['thread_id']
    )

    # Create index on created_at for message ordering
    op.create_index(
        'ix_chat_messages_created_at',
        'chat_messages',
        ['created_at'],
        postgresql_using='btree'
    )

    # Create composite index for efficient pagination queries
    op.create_index(
        'ix_chat_messages_thread_created',
        'chat_messages',
        ['thread_id', 'created_at'],
        postgresql_using='btree'
    )


def downgrade() -> None:
    """Drop chat_messages and chat_threads tables."""

    # Drop indexes first (chat_messages)
    op.drop_index('ix_chat_messages_thread_created', table_name='chat_messages')
    op.drop_index('ix_chat_messages_created_at', table_name='chat_messages')
    op.drop_index('ix_chat_messages_thread_id', table_name='chat_messages')

    # Drop chat_messages table
    op.drop_table('chat_messages')

    # Drop indexes (chat_threads)
    op.drop_index('ix_chat_threads_updated_at', table_name='chat_threads')
    op.drop_index('ix_chat_threads_user_id', table_name='chat_threads')

    # Drop chat_threads table
    op.drop_table('chat_threads')
