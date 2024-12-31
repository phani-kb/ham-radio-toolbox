from enum import Enum
from typing import Optional


class HRTEnum(Enum):
    """Base class for HRT enumerations (name = value)."""

    def __init__(self, eid: str, description: str = ""):
        self._id = eid
        self._description = description

    @property
    def id(self):
        """Get the id of the enumeration."""
        return self._id

    @property
    def description(self):
        return self._description

    def __str__(self):
        if self._description:
            return f"{self.id} - {self.description}"
        return self.id

    @classmethod
    def from_id(cls, eid: str) -> Optional["HRTEnum"]:
        """Get the enumeration from the given id."""
        return next((enum for enum in cls if enum.id == eid), None)

    @classmethod
    def from_name(cls, name: str) -> Optional["HRTEnum"]:
        """Get the enumeration from the given name."""
        return next((enum for enum in cls if enum.name == name), None)

    @classmethod
    def ids(cls) -> list[str]:
        """Get the ids for the enumeration."""
        return [enum.id for enum in cls]

    @classmethod
    def list(cls):
        """Get the list of the enumeration."""
        return [enum for enum in cls]
