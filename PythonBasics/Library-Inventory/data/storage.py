import os


class FileStorage:
    """JSON-backed persistence for the library inventory.

        Two files live next to this module:
          - library.json    : available books
          - borrowed.json   : borrowing records {book, borrower, timestamp}
    """

    _BASE = os.path.dirname(os.path.abspath(__file__))
    library_path = os.path.join(_BASE, "library.json")
    borrowed_path = os.path.join(_BASE, "borrowed.json")

    def __init__(self):
        self.books = [] # keeping track of all books
        self.borrowed = [] # keeping track of borrowed books



    def _persist(self):
        """persit data to disk."""
        pass


    @staticmethod
    def _read(path):
        """Reads JSON data from a file (disk) to memory."""
        pass

    @staticmethod
    def _write(path, data):
        """Writes JSON data to a file (disk)."""
        pass



    def load(self):
        """Loads books and borrowed records from JSON files (disk)."""
        pass

    def save(self):
        """Saves books and borrowed records to JSON files (disk)."""
        pass

    def delete(self):
        """Deletes books and borrowed records from JSON files (disk)"""
        pass


    def mark_borrowed(self, book, borrower):
        """Records that a book has been borrowed.
        remove it from the library. and add it to borrowed."""
        pass

    def mark_returned(self, book):
        """Records that a book has been returned.
        remove it from borrowed and add it to the library.
        """
        pass