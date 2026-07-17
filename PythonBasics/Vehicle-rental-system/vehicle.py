from abc import ABC, abstractmethod

_PREFIX_OWNERS = {}  # ID_PREFIX -> the class that claimed it


class Vehicle(ABC):
    """Base class for anything the shop can rent out.

    ``price`` is the stored base hourly price; ``renting_price`` is the
    derived hourly rate that subclasses compute from it (surcharge for
    heavy vehicles, discount for bikes, ...).

    Every vehicle gets a short unique ``id`` when it is created --- the
    class's ``ID_PREFIX`` plus a per-type counter, so cars are C1, C2, ...
    and trucks are T1, T2, ... Commands accept that id, which is what
    makes two same-named vehicles tellable apart.
    """

    ID_PREFIX = "V"
    _counter = 0

    def __init_subclass__(cls, **kwargs):
        """Give each subclass its own id counter and a distinct id prefix."""
        super().__init_subclass__(**kwargs)
        cls._counter = 0
        if "ID_PREFIX" not in cls.__dict__:
            cls.ID_PREFIX = cls.__name__[0].upper()
        owner = _PREFIX_OWNERS.get(cls.ID_PREFIX)
        if owner is not None:
            raise TypeError(
                f"ID_PREFIX '{cls.ID_PREFIX}' is already taken by {owner.__name__}; "
                f"give {cls.__name__} an explicit, distinct ID_PREFIX"
            )
        _PREFIX_OWNERS[cls.ID_PREFIX] = cls

    def __init__(self, name, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.name = name
        self._base_price = price
        cls = type(self)
        cls._counter += 1
        self.id = f"{cls.ID_PREFIX}{cls._counter}"

    @property
    @abstractmethod
    def renting_price(self):
        """Renting price per hour."""
        raise NotImplementedError(
            "subclasses of Vehicle must provide their renting_price implementation"
        )

    def rental_cost(self, hours):
        """Total cost of renting this vehicle for the given number of hours."""
        if hours < 0:
            raise ValueError("Hours cannot be negative")
        return self.renting_price * hours

    def __str__(self):
        return (
            f"[{self.id}] {type(self).__name__} '{self.name}' "
            f"(${self.renting_price:,.2f}/hour)"
        )

    def __eq__(self, other):
        if not isinstance(other, Vehicle):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Car(Vehicle):
    """Standard car, rented at its base hourly price."""

    ID_PREFIX = "C"

    @property
    def renting_price(self):
        return self._base_price


class Truck(Vehicle):
    """Heavy vehicle, rented with a 50% surcharge on the base price."""

    ID_PREFIX = "T"
    SURCHARGE = 1.5

    @property
    def renting_price(self):
        return self._base_price * self.SURCHARGE


class Bike(Vehicle):
    """Two-wheeler, rented at half the base price."""

    ID_PREFIX = "B"
    DISCOUNT = 0.5

    @property
    def renting_price(self):
        return self._base_price * self.DISCOUNT


VEHICLE_TYPES = (Car, Truck, Bike)
