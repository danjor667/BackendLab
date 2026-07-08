import cmd

from utils import (
    add_vehicle,
    rent_vehicle,
    return_vehicle,
    display_availability,
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
        "add <name> | <hourly price> [| car|truck|bike]"
        name, price, kind = _split(line, 3)
        if not (name and price):
            print("Usage: add <name> | <hourly price> [| car|truck|bike]")
            return
        add_vehicle(name, price, kind or "car")

    def do_rent(self, line):
        "rent <name> | <renter>"
        name, renter = _split(line, 2)
        if not (name and renter):
            print("Usage: rent <name> | <renter>")
            return
        rent_vehicle(name, renter)

    def do_return(self, line):
        "return <name> [| <renter>]"
        name, renter = _split(line, 2)
        if not name:
            print("Usage: return <name> [| <renter>]")
            return
        return_vehicle(name, renter)

    def do_list(self, _line):
        "list  — show the full inventory"
        display_availability()

    def do_quit(self, _line):
        "quit  — exit the rental system"
        print("Goodbye.")
        return True

    do_EOF = do_quit


if __name__ == "__main__":
    seed_initial_inventory()
    Console().cmdloop()
