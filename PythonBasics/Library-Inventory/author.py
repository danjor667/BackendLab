class Author:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other):
        if not isinstance(other, Author):
            return NotImplemented
        return self.name.lower() == other.name.lower()
