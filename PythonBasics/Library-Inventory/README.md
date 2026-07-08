# Library Inventory

An interactive command-line library tracker: add books to the shelf, search them, lend them out, and take them back. The inventory survives restarts — everything is persisted to JSON files on disk. Built as an exercise in object-oriented Python: abstract base classes, inheritance, polymorphic serialization, and file-based persistence.

## How it works

The app is a REPL built on Python's standard-library `cmd` module. Commands call helper functions in `utils.py`, which operate on a single `FileStorage` instance that keeps two collections in memory and mirrors every change to disk:

- **`data/library.json`** — books currently on the shelf (available)
- **`data/borrowed.json`** — loan records: `{book, borrower, timestamp}`

Borrowing moves a book from the shelf to the loan list; returning moves it back. On first launch the shelf is seeded with a few sample books.

### Resource model

`LibraryResource` is an abstract base class that defines the serialization contract: every resource must implement `to_dict()` (which stamps its class name under a `"type"` key) and `from_dict()`. The static factory `LibraryResource.deserialize(data)` reads that `"type"` tag and routes to the right subclass — so ebooks and audiobooks come back from JSON as the correct type.

```
LibraryResource (ABC)
└── Book
    ├── EBook       prints with an [EBOOK] prefix
    └── AudioBook   prints with an [AUDIOBOOK] prefix
```

Two books are considered the same if they share a title (case-insensitive) and published year — this is what prevents duplicate entries on the shelf.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Entry point — the `Console` REPL (built on `cmd.Cmd`) that parses commands |
| `book.py` | `LibraryResource` ABC and the `Book` / `EBook` / `AudioBook` types |
| `utils.py` | Command implementations: add, search, borrow, return, list, seed |
| `data/storage.py` | `FileStorage` — in-memory collections mirrored to the JSON files |
| `data/library.json` | Persisted shelf (created automatically) |
| `data/borrowed.json` | Persisted loan records (created automatically) |
| `author.py`, `borrower.py` | `Author` and `Borrower` value classes (name + case-insensitive equality) |

## Requirements

- Python 3.11+
- No runtime dependencies (Poetry is used for project management; `black` is a dev tool)

## Running

```bash
cd PythonBasics/Library-Inventory
python main.py
```

Or with Poetry:

```bash
poetry install
poetry run python main.py
```

## Commands

Arguments with multiple fields are separated by a pipe (`|`):

| Command | Description |
| --- | --- |
| `add <title> \| <author> \| <year> [\| book\|ebook\|audiobook]` | Shelve a new book (kind defaults to `book`) |
| `search <keyword>` | Match keyword against title or author; blank keyword lists everything |
| `borrow <title> \| <borrower>` | Lend an available book to someone |
| `return <title> [\| <borrower>]` | Return a book; borrower narrows the match if several people could have it |
| `list` | Show the full inventory: shelf + who has what |
| `quit` (or Ctrl-D) | Exit |

## Example session

```
>> add Refactoring | Martin Fowler | 1999 | ebook
Added: [EBOOK] "Refactoring" by Martin Fowler (1999)
>> borrow Refactoring | Dana
Dana borrowed [EBOOK] "Refactoring" by Martin Fowler (1999)
>> list
On the shelf (4):
  "The Pragmatic Programmer" by Andrew Hunt (1999)
  [EBOOK] "Fluent Python" by Luciano Ramalho (2015)
  [AUDIOBOOK] "Clean Code" by Robert C. Martin (2008)
  [EBOOK] "The Art of Computer Programming" by Donald Knuth (2002)
Borrowed (1):
  [EBOOK] "Refactoring" by Martin Fowler (1999) -> Dana (2026-07-07T10:15:00)
>> search fowler
  [borrowed by Dana] [EBOOK] "Refactoring" by Martin Fowler (1999)
>> return Refactoring | Dana
Returned: [EBOOK] "Refactoring" by Martin Fowler (1999)
>> quit
Goodbye.
```

## API overview

### `LibraryResource` (abstract, `book.py`)

- `to_dict()` *(abstract)* — serialize to a plain dict, tagging the subtype under `"type"`.
- `from_dict(data)` *(abstract classmethod)* — rebuild an instance from a dict; subclasses inherit one implementation that constructs `cls`.
- `deserialize(data)` *(static factory)* — look up the `"type"` tag in the resource registry and dispatch to the matching subclass's `from_dict` (falls back to `Book`).

### `Book` / `EBook` / `AudioBook`

- `Book(title, author, published_year)` — the concrete resource; `EBook` and `AudioBook` only override `__str__` for their display prefix.
- Equality is case-insensitive title + published year, used for duplicate detection.

### `FileStorage` (`data/storage.py`)

- `load()` — read both JSON files into memory, deserializing each book to its proper subtype.
- `save(book)` — shelve a book unless an equal one already exists; returns `True`/`False`.
- `delete(book)` — remove a book from the shelf.
- `mark_borrowed(book, borrower, timestamp)` — move a book from the shelf to the loan list.
- `mark_returned(record)` — move a loan record's book back to the shelf.

Every mutating call re-writes both JSON files, so the on-disk state always matches memory.

### Command helpers (`utils.py`)

- `add_book(title, author, year, kind)` — create the right resource type and shelve it.
- `search_books(keyword)` — case-insensitive match on title or author, across shelf and loans.
- `borrow_book(title, borrower)` / `return_book(title, borrower)` — move books between shelf and loans.
- `list_inventory()` — print the shelf and current loans.
- `seed_initial_inventory()` — populate a few sample books when both files are empty.

## Extending

To add a new resource type (say, a magazine), subclass `Book` (or `LibraryResource` directly for a different shape), add it to the `RESOURCE_TYPES` tuple in `book.py` so `deserialize` can find it, and register a command alias in `_BOOK_TYPES` usage by picking a kind name — `add_book(..., kind="magazine")` resolves the class by lowercase class name:

```python
class Magazine(Book):
    def __str__(self):
        return f"[MAGAZINE] {super().__str__()}"

RESOURCE_TYPES = (Book, EBook, AudioBook, Magazine)
```
