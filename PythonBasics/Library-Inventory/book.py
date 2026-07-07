from abc import ABC, abstractmethod


class LibraryResource(ABC):
    """Base type for anything the library can hold.

    Both directions of serialization are part of the contract:
      - ``to_dict``   : abstract — each concrete resource serializes itself,
        stamping its class name under ``type`` so the subtype can be recovered.
      - ``from_dict`` : abstract classmethod — each concrete resource rebuilds
        itself from a dict. Because it is a classmethod, subclasses inherit a
        single implementation that constructs ``cls``.
      - ``deserialize``: concrete factory that reads the ``type`` tag and routes
        to the matching subtype's ``from_dict``.
    """

    @abstractmethod
    def to_dict(self): ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data): ...

    @staticmethod
    def deserialize(data):
        """Build the correct resource subtype from its ``type`` (class name) tag."""
        registry = {cls.__name__: cls for cls in RESOURCE_TYPES}
        cls = registry.get(data.get("type"), Book)
        return cls.from_dict(data)


class Book(LibraryResource):

    def __init__(self, title, author, published_year):
        self.title = title
        self.author = author
        self.published_year = published_year

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "title": self.title,
            "author": self.author,
            "published_year": self.published_year,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["title"], data["author"], data["published_year"])

    def __str__(self):
        return f'"{self.title}" by {self.author} ({self.published_year})'

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.title.lower() == other.title.lower() and str(
            self.published_year
        ) == str(other.published_year)


class EBook(Book):

    def __str__(self):
        return f"[EBOOK] {super().__str__()}"


class AudioBook(Book):

    def __str__(self):
        return f"[AUDIOBOOK] {super().__str__()}"


RESOURCE_TYPES = (Book, EBook, AudioBook)
