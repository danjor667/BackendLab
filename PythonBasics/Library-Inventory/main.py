import cmd

from utils import (
    add_book,
    search_books,
    borrow_book,
    return_book,
    list_inventory,
    seed_initial_inventory,
)


def _split(line, count):
    """Split a pipe-delimited command line into exactly `count` parts (padded)."""
    parts = [p.strip() for p in line.split("|")]
    parts += [""] * (count - len(parts))
    return parts[:count]


class Console(cmd.Cmd):
    prompt = ">> "

    def do_add(self, line):
        "add <title> | <author> | <year> [| book|ebook|audiobook]"
        title, author, year, kind = _split(line, 4)
        if not (title and author and year):
            print("Usage: add <title> | <author> | <year> [| book|ebook|audiobook]")
            return
        add_book(title, author, year, kind or "book")

    def do_search(self, word):
        "search <keyword>  — match title or author (blank lists everything)"
        search_books(word)

    def do_borrow(self, line):
        "borrow <title> | <borrower>"
        title, borrower = _split(line, 2)
        if not (title and borrower):
            print("Usage: borrow <title> | <borrower>")
            return
        borrow_book(title, borrower)

    def do_return(self, line):
        "return <title> [| <borrower>]"
        title, borrower = _split(line, 2)
        if not title:
            print("Usage: return <title> [| <borrower>]")
            return
        return_book(title, borrower)

    def do_list(self, _line):
        "list  — show the full inventory"
        list_inventory()

    def do_quit(self, _line):
        "quit  — exit the tracker"
        print("Goodbye.")
        return True

    do_EOF = do_quit


if __name__ == "__main__":
    seed_initial_inventory()
    Console().cmdloop()
