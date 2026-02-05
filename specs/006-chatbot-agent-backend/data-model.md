# Data Model: Chatbot Backend

**Feature**: 006-chatbot-agent-backend
**Date**: 2026-02-02
**Source**: Extracted from spec.md Key Entities and Phase 0 Decision 6

---

## Entity Relationship Diagram

```
User (existing)
  │
  │ (1:N)
  ▼
ChatThread
  │
  │ (1:N)
  ▼
ChatMessage
```

---

## Entities

### 1. ChatThread

**Purpose**: Represents a conversation session between a user and the AI assistant.

**Attributes**:
- `id` (TEXT, PRIMARY KEY): UUID for global uniqueness
- `user_id` (TEXT, NOT NULL, FK → user.id): Owner of the conversation
- `title` (TEXT, NULL): Optional conversation title (e.g., "Task Planning Discussion")
- `created_at` (TIMESTAMP, NOT NULL): Thread creation timestamp
- `updated_at` (TIMESTAMP, NOT NULL): Last message timestamp (updated on each message)

**Relationships**:
- **Belongs to**: User (via `user_id`)
- **Has many**: ChatMessage (via `thread_id`)

**Indexes**:
- `idx_chat_threads_user_id` on `user_id` (for efficient user thread listing)

**Constraints**:
- `user_id` FOREIGN KEY REFERENCES user(id) ON DELETE CASCADE
- `id` generated via UUID4

**Lifecycle**:
- Created: When user sends first message without `thread_id` parameter
- Updated: `updated_at` timestamp refreshed on each new message
- Deleted: Automatically removed when user account is deleted (CASCADE)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class ChatThread(SQLModel, table=True):
    __tablename__ = "chat_threads"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: list["ChatMessage"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

---

### 2. ChatMessage

**Purpose**: Represents a single message in a conversation thread (user message, assistant response, or system message).

**Attributes**:
- `id` (BIGSERIAL, PRIMARY KEY): Auto-incrementing integer for sequential ordering
- `thread_id` (TEXT, NOT NULL, FK → chat_threads.id): Thread this message belongs to
- `role` (TEXT, NOT NULL, CHECK): Message sender role ('user' | 'assistant' | 'system')
- `content` (TEXT, NOT NULL): Message text content
- `created_at` (TIMESTAMP, NOT NULL): Message timestamp

**Relationships**:
- **Belongs to**: ChatThread (via `thread_id`)

**Indexes**:
- `idx_chat_messages_thread_id` on `thread_id` (for efficient thread message loading)
- `idx_chat_messages_created_at` on `created_at` (for chronological ordering)
- Composite index on `(thread_id, created_at)` for optimized pagination queries

**Constraints**:
- `thread_id` FOREIGN KEY REFERENCES chat_threads(id) ON DELETE CASCADE
- `role` CHECK CONSTRAINT: `role IN ('user', 'assistant', 'system')`

**Lifecycle**:
- Created: When user sends message or assistant generates response
- Immutable: Messages are never updated after creation
- Deleted: Automatically removed when thread is deleted (CASCADE)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from datetime import datetime
from sqlalchemy import CheckConstraint

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_role"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-increment
    thread_id: str = Field(foreign_key="chat_threads.id", index=True)
    role: str  # Enum enforced by CHECK constraint
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    thread: ChatThread = Relationship(back_populates="messages")
```

---

### 3. RequestContext (Runtime Object)

**Purpose**: Per-request authentication and configuration object passed through ChatKit and Agent execution.

**Attributes**:
- `user_id` (str): Extracted from JWT 'sub' claim
- `token` (str): Full JWT token (Bearer format) for MCP server forwarding
- `request` (Request): FastAPI Request object for additional context

**Relationships**:
- Used by NeonPostgresStore for user_id filtering
- Used by agent_factory to create per-user Agent instances
- Passed to MCP client for Authorization headers

**Lifecycle**:
- Created: At start of each `/api/chatkit` request after JWT verification
- Exists: Only in memory during request processing
- Destroyed: Request completion

**Python Definition**:
```python
from dataclasses import dataclass
from fastapi import Request

@dataclass
class RequestContext:
    """Per-request authentication and configuration context"""
    user_id: str
    token: str  # Full "Bearer ..." string
    request: Request
```

---

## Database Migration

**Alembic Migration**: `alembic/versions/001_create_chat_tables.py`

```python
"""Create chat_threads and chat_messages tables

Revision ID: 001_create_chat_tables
Revises:
Create Date: 2026-02-02
"""
from alembic import op
import sqlalchemy as sa

revision = '001_create_chat_tables'
down_revision = None  # First migration for chatbot backend
branch_labels = None
depends_on = None

def upgrade():
    # Create chat_threads table
    op.create_table(
        'chat_threads',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('user_id', sa.Text(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('idx_chat_threads_user_id', 'chat_threads', ['user_id'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('thread_id', sa.Text(), sa.ForeignKey('chat_threads.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_role'),
    )
    op.create_index('idx_chat_messages_thread_id', 'chat_messages', ['thread_id'])
    op.create_index('idx_chat_messages_created_at', 'chat_messages', ['created_at'])

def downgrade():
    op.drop_index('idx_chat_messages_created_at', 'chat_messages')
    op.drop_index('idx_chat_messages_thread_id', 'chat_messages')
    op.drop_table('chat_messages')

    op.drop_index('idx_chat_threads_user_id', 'chat_threads')
    op.drop_table('chat_threads')
```

---

## Data Isolation Patterns

### User-Scoped Queries

**All queries MUST filter by user_id** to enforce data isolation (FR-004, SC-003):

```python
# Load user's threads (NeonPostgresStore.load_thread)
async def load_thread(self, thread_id: str, context: RequestContext) -> ThreadMetadata:
    stmt = select(ChatThread).where(
        ChatThread.id == thread_id,
        ChatThread.user_id == context.user_id  # CRITICAL: User isolation
    )
    # Returns NotFoundError if thread doesn't exist OR doesn't belong to user

# List user's threads (sorted by most recent)
async def list_user_threads(self, user_id: str, limit: int = 10) -> list[ChatThread]:
    stmt = (
        select(ChatThread)
        .where(ChatThread.user_id == user_id)
        .order_by(ChatThread.updated_at.desc())
        .limit(limit)
    )

# Load thread messages (already isolated via thread_id ownership)
async def load_thread_items(
    self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
) -> Page[ThreadItem]:
    # First verify thread belongs to user
    thread = await self.load_thread(thread_id, context)

    # Then load messages
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread_id)
        .order_by(ChatMessage.created_at.asc() if order == "asc" else ChatMessage.created_at.desc())
        .limit(limit)
    )
```

### Cross-User Access Prevention

**Attempting to access another user's data returns 404 Not Found** (not 403 Forbidden):
- Prevents attackers from enumerating valid thread IDs
- Identical behavior whether thread doesn't exist or unauthorized
- Satisfies Constitution Principle VII (Stateless Security)

---

## Performance Considerations

### Indexing Strategy

1. **user_id index** (chat_threads):
   - Query: "List all threads for user X"
   - Cardinality: Thousands of users, dozens of threads per user
   - Benefit: O(log n) thread discovery vs O(n) full table scan

2. **thread_id index** (chat_messages):
   - Query: "Load messages for thread X"
   - Cardinality: Hundreds of threads, dozens to hundreds of messages per thread
   - Benefit: O(log n) message loading

3. **created_at index** (chat_messages):
   - Query: "Load last 20 messages" (chronological pagination)
   - Cardinality: Timestamp on every message
   - Benefit: Efficient ORDER BY created_at DESC

4. **Composite (thread_id, created_at)** index:
   - Query: "Load messages for thread X ordered by time"
   - Benefit: Covers both WHERE and ORDER BY in single index lookup
   - Trade-off: Additional storage for composite index vs two separate lookups

### Pagination Strategy

```python
# Load last 20 messages for thread
async def load_recent_messages(self, thread_id: str, limit: int = 20) -> list[ChatMessage]:
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.thread_id == thread_id)
        .order_by(ChatMessage.created_at.desc())  # Most recent first
        .limit(limit)
    )
    # Returns messages newest-to-oldest, frontend can reverse if needed
```

### Thread Message Count Estimation

For threads with 100+ messages (SC-009), consider:
- Lazy loading with pagination (load 20 at a time)
- Cursor-based pagination using message ID
- Avoid COUNT(*) queries on large result sets

---

## Validation Rules

### ChatThread Validation
- `id`: Must be valid UUID4 format
- `user_id`: Must reference existing user.id
- `title`: Optional, max length 200 characters (enforced at application layer)
- `created_at`, `updated_at`: Auto-managed by database

### ChatMessage Validation
- `thread_id`: Must reference existing chat_threads.id
- `role`: Must be one of ('user', 'assistant', 'system') - enforced by CHECK constraint
- `content`: Required, not empty (enforced at application layer)
- `created_at`: Auto-managed by database

### RequestContext Validation
- `user_id`: Must be non-empty string extracted from valid JWT
- `token`: Must start with "Bearer " prefix
- `request`: Must be FastAPI Request object

---

## Data Retention

**Current Implementation**: Indefinite retention (messages never auto-deleted)

**Future Considerations** (Out of Scope for this phase):
- Thread archival after N days of inactivity
- Message pruning for threads exceeding size limits
- User-initiated thread deletion
- GDPR compliance (user data export/deletion requests)

---

## Testing Data

### Sample Thread

```python
thread = ChatThread(
    id="550e8400-e29b-41d4-a716-446655440000",
    user_id="SPYX2uSMwyTPRiair7PL6EcFS7Otkis2",
    title="Task Planning Discussion",
    created_at=datetime(2026, 2, 2, 10, 0, 0),
    updated_at=datetime(2026, 2, 2, 10, 5, 30)
)
```

### Sample Messages

```python
messages = [
    ChatMessage(
        id=1,
        thread_id="550e8400-e29b-41d4-a716-446655440000",
        role="user",
        content="Show me my incomplete tasks",
        created_at=datetime(2026, 2, 2, 10, 0, 0)
    ),
    ChatMessage(
        id=2,
        thread_id="550e8400-e29b-41d4-a716-446655440000",
        role="assistant",
        content="You have 3 incomplete tasks:\n1. Buy groceries\n2. Finish project report\n3. Call dentist",
        created_at=datetime(2026, 2, 2, 10, 0, 5)
    ),
    ChatMessage(
        id=3,
        thread_id="550e8400-e29b-41d4-a716-446655440000",
        role="user",
        content="Mark task 1 as complete",
        created_at=datetime(2026, 2, 2, 10, 5, 20)
    ),
    ChatMessage(
        id=4,
        thread_id="550e8400-e29b-41d4-a716-446655440000",
        role="assistant",
        content="✓ Task 'Buy groceries' has been marked as complete!",
        created_at=datetime(2026, 2, 2, 10, 5, 30)
    ),
]
```
