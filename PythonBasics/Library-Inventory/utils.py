from datetime import datetime

from book import Book, EBook, AudioBook, RESOURCE_TYPES
from data.storage import FileStorage

storage = FileStorage()
storage.load()

_BOOK_TYPES = {cls.__name__.lower(): cls for cls in RESOURCE_TYPES}

# How many finished loans `report` lists before it stops and says so.
RECENT_RETURNS = 10


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
    else:
        print(f"Invalid year: '{published_year}'")
        return None
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
            storage.mark_returned(record, datetime.now().isoformat(timespec="seconds"))
            print(f"Returned: {record['book']}")
            return record["book"]
    print(f"No borrowed copy of '{title}' found for {borrower or 'anyone'}.")
    return None


def _parse_timestamp(value):
    """Parse a stored ISO timestamp, or None if it is missing or malformed."""
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _days_held(borrowed_at, returned_at=None):
    """Days a book was (or has been) kept. None if the timestamps are unusable.

    An open loan is measured against now, so it grows until the book comes back.
    """
    start = _parse_timestamp(borrowed_at)
    if start is None:
        return None
    end = _parse_timestamp(returned_at) if returned_at else datetime.now()
    if end is None:
        return None
    return (end - start).total_seconds() / 86400


def _format_days(days):
    return "unknown" if days is None else f"{days:.1f} days"


def _format_date(value):
    stamp = _parse_timestamp(value)
    return stamp.strftime("%Y-%m-%d") if stamp else "unknown"


def report():
    """Print a borrowing report: current loans, past returns, and days held."""
    active, history = storage.borrowed, storage.history
    total_loans = len(active) + len(history)

    durations = [
        days
        for days in (_days_held(r["borrowed_at"], r["returned_at"]) for r in history)
        if days is not None
    ]
    average = sum(durations) / len(durations) if durations else None

    title = "Library report"
    lines = [
        title,
        "=" * len(title),
        f"{'On shelf:':<19}{len(storage.books)}",
        f"{'On loan:':<19}{len(active)}",
        f"{'Loans all time:':<19}{total_loans}",
        f"{'Returned:':<19}{len(history)}",
        f"{'Average days held:':<19}{f'{average:.1f}' if average is not None else '-'}",
    ]

    if active:
        # Longest-held first: whoever has had a book the longest is the most
        # interesting line in the report.
        ordered = sorted(
            active,
            key=lambda r: _days_held(r["timestamp"]) or -1.0,
            reverse=True,
        )
        heading = f"Currently borrowed ({len(active)})"
        lines += ["", heading, "-" * len(heading)]
        for record in ordered:
            held = _format_days(_days_held(record["timestamp"]))
            since = _format_date(record["timestamp"])
            lines.append(f"  {record['book']}")
            lines.append(f"    {record['borrower']} - {held} so far (since {since})")

    if history:
        recent = sorted(history, key=lambda r: r["returned_at"], reverse=True)
        shown = recent[:RECENT_RETURNS]
        heading = (
            f"Recent returns (latest {len(shown)} of {len(history)})"
            if len(history) > len(shown)
            else f"Recent returns ({len(history)})"
        )
        lines += ["", heading, "-" * len(heading)]
        for record in shown:
            held = _format_days(
                _days_held(record["borrowed_at"], record["returned_at"])
            )
            span = f"{_format_date(record['borrowed_at'])} -> {_format_date(record['returned_at'])}"
            lines.append(f"  {record['book']}")
            lines.append(f"    {record['borrower']} - held {held} ({span})")

    if not total_loans:
        lines += ["", "No loans recorded yet."]

    print("\n".join(lines))
    return {
        "on_shelf": len(storage.books),
        "on_loan": len(active),
        "total_loans": total_loans,
        "returned": len(history),
        "average_days_held": average,
    }


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
