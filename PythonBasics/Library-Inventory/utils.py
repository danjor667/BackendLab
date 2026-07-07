from datetime import datetime

from book import Book, EBook, AudioBook, RESOURCE_TYPES
from data.storage import FileStorage

storage = FileStorage()
storage.load()

_BOOK_TYPES = {cls.__name__.lower(): cls for cls in RESOURCE_TYPES}


def seed_initial_inventory():
    """Populate the shelf with a few books the first time the app runs."""
    if storage.books or storage.borrowed:
        return
    samples = [
        Book("The Pragmatic Programmer", "Andrew Hunt", 1999),
        EBook("Fluent Python", "Luciano Ramalho", 2015),
        AudioBook("Clean Code", "Robert C. Martin", 2008),
        EBook("The Art of Computer Programming", "Donald Knuth", 2002),
    ]
    for book in samples:
        storage.save(book)


def add_book(title, author, published_year, kind="book"):
    """Create and shelve a book. Returns the created Book, or None if it exists."""
    cls = _BOOK_TYPES.get(kind.lower(), Book)
    if isinstance(published_year, str) and published_year.strip().isdigit():
        published_year = int(published_year)
    book = cls(title, author, published_year)
    if storage.save(book):
        print(f"Added: {book}")
        return book
    print(f"Already on the shelf: {book}")
    return None


def search_books(keyword):
    """Print every available/borrowed book matching keyword in title or author."""
    keyword = (keyword or "").strip().lower()
    if not keyword:
        return list_inventory()

    def matches(book):
        return keyword in book.title.lower() or keyword in book.author.lower()

    available = [b for b in storage.books if matches(b)]
    out = [r for r in storage.borrowed if matches(r["book"])]

    if not available and not out:
        print(f"No books matching '{keyword}'.")
        return []

    for book in available:
        print(f"  [available] {book}")
    for record in out:
        print(f"  [borrowed by {record['borrower']}] {record['book']}")
    return available


def _find_available(title):
    title = title.strip().lower()
    for book in storage.books:
        if book.title.lower() == title:
            return book
    return None


def borrow_book(title, borrower):
    """Move a book from the shelf to a borrower."""
    book = _find_available(title)
    if book is None:
        print(f"Not available to borrow: '{title}'")
        return None
    storage.mark_borrowed(book, borrower, datetime.now().isoformat(timespec="seconds"))
    print(f"{borrower} borrowed {book}")
    return book


def _matches_loan(record, title_key, borrower):
    """True if a borrowing record matches the title (and borrower, if given)."""
    if record["book"].title.lower() != title_key:
        return False
    if not borrower:
        return True  # no borrower filter -> matches whoever has it
    return record["borrower"].lower() == borrower.lower()


def return_book(title, borrower):
    """Return a borrowed book to the shelf."""
    title_key = title.strip().lower()
    for record in storage.borrowed:
        if _matches_loan(record, title_key, borrower):
            storage.mark_returned(record)
            print(f"Returned: {record['book']}")
            return record["book"]
    print(f"No borrowed copy of '{title}' found for {borrower or 'anyone'}.")
    return None


def list_inventory():
    """Print the full inventory: shelf + borrowed."""
    if not storage.books and not storage.borrowed:
        print("The library is empty.")
        return []
    print(f"On the shelf ({len(storage.books)}):")
    for book in storage.books:
        print(f"  {book}")
    if storage.borrowed:
        print(f"Borrowed ({len(storage.borrowed)}):")
        for record in storage.borrowed:
            print(f"  {record['book']} -> {record['borrower']} ({record['timestamp']})")
    return storage.books
