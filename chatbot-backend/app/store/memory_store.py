"""In-memory implementation of ChatKit Store interface.

This module provides a simple in-memory store for development and testing.
Production deployments should use NeonPostgresStore (Phase 5).
"""

from collections import defaultdict

from chatkit.store import Store, NotFoundError
from chatkit.types import ThreadMetadata, ThreadItem, Attachment, Page

from app.models.request_context import RequestContext


class InMemoryStore(Store[RequestContext]):
    """Simple in-memory store for chat data.

    This store keeps all data in memory and does not persist across restarts.
    It's suitable for Phase 3 (US1) basic chat functionality testing.

    Attributes:
        threads: Dictionary mapping thread_id to ThreadMetadata
        items: Dictionary mapping thread_id to list of ThreadItems
        attachments: Dictionary mapping attachment_id to Attachment
    """

    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = defaultdict(list)
        self.attachments: dict[str, Attachment] = {}

    async def load_thread(
        self, thread_id: str, context: RequestContext
    ) -> ThreadMetadata:
        """Load thread metadata by ID.

        Args:
            thread_id: Thread identifier
            context: Request context with user_id for isolation

        Returns:
            ThreadMetadata: Thread metadata

        Raises:
            NotFoundError: Thread not found or doesn't belong to user
        """
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")

        thread = self.threads[thread_id]
        # User isolation check would go here in production
        # For Phase 3, we're not enforcing it strictly in memory
        return thread

    async def save_thread(
        self, thread: ThreadMetadata, context: RequestContext
    ) -> None:
        """Persist thread metadata.

        Args:
            thread: Thread metadata to save
            context: Request context with user_id
        """
        self.threads[thread.id] = thread

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        """Load paginated list of threads.

        Args:
            limit: Maximum threads to return
            after: Cursor for pagination (thread ID)
            order: Sort order ("asc" or "desc")
            context: Request context

        Returns:
            Page[ThreadMetadata]: Paginated threads
        """
        threads = list(self.threads.values())
        sorted_threads = sorted(
            threads,
            key=lambda t: t.created_at,
            reverse=(order == "desc")
        )

        # Handle pagination
        start = 0
        if after:
            for idx, thread in enumerate(sorted_threads):
                if thread.id == after:
                    start = idx + 1
                    break

        data = sorted_threads[start:start + limit]
        has_more = start + limit < len(sorted_threads)
        next_after = data[-1].id if has_more and data else None

        return Page(data=data, has_more=has_more, after=next_after)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Page[ThreadItem]:
        """Load paginated thread items.

        Args:
            thread_id: Thread identifier
            after: Cursor for pagination (item ID)
            limit: Maximum items to return
            order: Sort order ("asc" or "desc")
            context: Request context

        Returns:
            Page[ThreadItem]: Paginated items
        """
        items = self.items.get(thread_id, [])
        sorted_items = sorted(
            items,
            key=lambda i: i.created_at,
            reverse=(order == "desc")
        )

        # Handle pagination
        start = 0
        if after:
            for idx, item in enumerate(sorted_items):
                if item.id == after:
                    start = idx + 1
                    break

        data = sorted_items[start:start + limit]
        has_more = start + limit < len(sorted_items)
        next_after = data[-1].id if has_more and data else None

        return Page(data=data, has_more=has_more, after=next_after)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        """Add new item to thread.

        Args:
            thread_id: Thread identifier
            item: Thread item to add
            context: Request context
        """
        self.items[thread_id].append(item)

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        """Upsert thread item by ID.

        Args:
            thread_id: Thread identifier
            item: Thread item to save
            context: Request context
        """
        items = self.items[thread_id]
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                return
        items.append(item)

    async def load_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> ThreadItem:
        """Load specific thread item.

        Args:
            thread_id: Thread identifier
            item_id: Item identifier
            context: Request context

        Returns:
            ThreadItem: Thread item

        Raises:
            NotFoundError: Item not found
        """
        for item in self.items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found")

    async def delete_thread(
        self, thread_id: str, context: RequestContext
    ) -> None:
        """Delete thread and all items.

        Args:
            thread_id: Thread identifier
            context: Request context
        """
        self.threads.pop(thread_id, None)
        self.items.pop(thread_id, None)

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> None:
        """Delete specific thread item.

        Args:
            thread_id: Thread identifier
            item_id: Item identifier
            context: Request context
        """
        self.items[thread_id] = [
            i for i in self.items.get(thread_id, [])
            if i.id != item_id
        ]

    async def save_attachment(
        self, attachment: Attachment, context: RequestContext
    ) -> None:
        """Persist attachment metadata.

        Args:
            attachment: Attachment to save
            context: Request context
        """
        self.attachments[attachment.id] = attachment

    async def load_attachment(
        self, attachment_id: str, context: RequestContext
    ) -> Attachment:
        """Load attachment by ID.

        Args:
            attachment_id: Attachment identifier
            context: Request context

        Returns:
            Attachment: Attachment metadata

        Raises:
            NotFoundError: Attachment not found
        """
        if attachment_id not in self.attachments:
            raise NotFoundError(f"Attachment {attachment_id} not found")
        return self.attachments[attachment_id]

    async def delete_attachment(
        self, attachment_id: str, context: RequestContext
    ) -> None:
        """Delete attachment.

        Args:
            attachment_id: Attachment identifier
            context: Request context
        """
        self.attachments.pop(attachment_id, None)
