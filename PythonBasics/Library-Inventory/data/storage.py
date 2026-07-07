import json
import os
from book import Book, LibraryResource


class FileStorage:
    """JSON-backed persistence for the library inventory.

    Two files live next to this module:
      - library.json    : available books
      - borrowed.json   : borrowing records {book, borrower, timestamp}
    """

    _BASE = os.path.dirname(os.path.abspath(__file__))
    print(_BASE)
    library_path = os.path.join(_BASE, "library.json")
    borrowed_path = os.path.join(_BASE, "borrowed.json")

    def __init__(self):
        self.books = (
            []
        )  # keeping track of all books (books obj): maybe use a set instead of a list?
        self.borrowed = (
            []
        )  # track of borrowed books:  store as {"book": Book, "borrower": str, "timestamp": str}

    def _persist(self):
        """persit data to disk."""
        books = [book.to_dict() for book in self.books]
        borrowed = [
            {
                "book": record["book"].to_dict(),
                "borrower": record["borrower"],
                "timestamp": record["timestamp"],
            }
            for record in self.borrowed
        ]
        self._write(self.library_path, books)
        self._write(self.borrowed_path, borrowed)

    @staticmethod
    def _read(path):
        """Reads JSON data from a file (disk) to memory."""
        try:
            with open(path, "r") as f:
                contents = f.read().strip()
                return json.loads(contents) if contents else []
        except FileNotFoundError:
            return []

    @staticmethod
    def _write(path, data):
        """Writes JSON data to a file (disk)."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        """Loads books and borrowed records from JSON files (disk)."""
        self.books = [
            LibraryResource.deserialize(b) for b in self._read(self.library_path)
        ]
        self.borrowed = [
            {
                "book": LibraryResource.deserialize(b["book"]),
                "borrower": b["borrower"],
                "timestamp": b["timestamp"],
            }
            for b in self._read(self.borrowed_path)
        ]

    def save(self, book: Book):
        """Saves books and borrowed records to JSON files (disk)."""
        if book in self.books:
            return False
        self.books.append(book)
        self._persist()
        return True

    def delete(self, book: Book):
        """Deletes books and borrowed records from JSON files (disk)"""
        if book not in self.books:
            return False
        self.books.remove(book)
        self._persist()
        return True

    def mark_borrowed(self, book: Book, borrower: str, timestamp: str = ""):
        """Records that a book has been borrowed.
        remove it from the library. and add it to borrowed."""
        self.books.remove(book)
        self.borrowed.append(
            {"book": book, "borrower": borrower, "timestamp": timestamp}
        )
        self._persist()
        return True

    def mark_returned(self, record: dict):
        """Records that a book has been returned.
        remove it from borrowed and add it to the library.
        """
        self.borrowed.remove(record)
        self.books.append(record["book"])
        self._persist()
        return True
