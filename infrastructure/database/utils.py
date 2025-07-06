from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


class UUIDMixin:
    """
    Mixin to create UUID primary key
    """

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampsMixin:
    """
    Mixin to create timestamp fields for creation, update, and deletion
    """

    created = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    deleted = Column(DateTime(timezone=True), default=None)
    updated = Column(DateTime(timezone=True), default=None)

    def delete(self):
        """
        Mixin method to set timestamp for deletion
        """
        self.deleted = datetime.now(timezone.utc)

    def update(self):
        """
        Mixin method to set timestamp for update
        """
        self.updated = datetime.now(timezone.utc)
