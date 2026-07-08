from abc import ABC, abstractmethod


class Vehicle(ABC):
    """Base class for anything the shop can rent out.

    ``price`` is the stored base hourly price; ``renting_price`` is the
    derived hourly rate that subclasses compute from it (surcharge for
    heavy vehicles, discount for bikes, ...).
    """

    def __init__(self, name, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.name = name
        self._base_price = price

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
        return f"{type(self).__name__} '{self.name}' (${self.renting_price:,.2f}/hour)"

    def __eq__(self, other):
        if not isinstance(other, Vehicle):
            return NotImplemented
        return type(self) is type(other) and self.name.lower() == other.name.lower()


class Car(Vehicle):
    """Standard car, rented at its base hourly price."""

    @property
    def renting_price(self):
        return self._base_price


class Truck(Vehicle):
    """Heavy vehicle, rented with a 50% surcharge on the base price."""

    SURCHARGE = 1.5

    @property
    def renting_price(self):
        return self._base_price * self.SURCHARGE


class Bike(Vehicle):
    """Two-wheeler, rented at half the base price."""

    DISCOUNT = 0.5

    @property
    def renting_price(self):
        return self._base_price * self.DISCOUNT


VEHICLE_TYPES = (Car, Truck, Bike)
