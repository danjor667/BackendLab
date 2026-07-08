import math
from datetime import datetime

from vehicle import Car, Truck, Bike, VEHICLE_TYPES

_VEHICLE_KINDS = {cls.__name__.lower(): cls for cls in VEHICLE_TYPES}

available = []  # vehicles in the garage, ready to rent
rented = []  # rental records: {"vehicle": Vehicle, "renter": str, "timestamp": str}


def seed_initial_inventory():
    """Populate the garage with a few vehicles the first time the app runs."""
    if available or rented:
        return
    samples = [
        Car("Toyota Corolla", 20),
        Car("Honda Civic", 22),
        Truck("Ford F-150", 40),
        Bike("Yamaha MT-07", 18),
    ]
    available.extend(samples)


def add_vehicle(name, price, kind="car"):
    """Create and garage a vehicle. Returns it, or None if it already exists."""
    cls = _VEHICLE_KINDS.get(kind.lower(), Car)
    if isinstance(price, str):
        try:
            price = float(price)
        except ValueError:
            print(f"Invalid price: '{price}'")
            return None
    vehicle = cls(name, price)
    if vehicle in available or any(r["vehicle"] == vehicle for r in rented):
        print(f"Already in the garage: {vehicle}")
        return None
    available.append(vehicle)
    print(f"Added: {vehicle}")
    return vehicle


def _find_available(name):
    name = name.strip().lower()
    for vehicle in available:
        if vehicle.name.lower() == name:
            return vehicle
    return None


def rent_vehicle(name, renter):
    """Move a vehicle from the garage to a renter."""
    vehicle = _find_available(name)
    if vehicle is None:
        print(f"Not available to rent: '{name}'")
        return None
    available.remove(vehicle)
    rented.append(
        {
            "vehicle": vehicle,
            "renter": renter,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
    )
    print(f"{renter} rented {vehicle}")
    return vehicle


def _matches_rental(record, name_key, renter):
    """True if a rental record matches the vehicle name (and renter, if given)."""
    if record["vehicle"].name.lower() != name_key:
        return False
    if not renter:
        return True  # no renter filter -> matches whoever has it
    return record["renter"].lower() == renter.lower()


def _billable_hours(rented_at, returned_at):
    """Hours to bill for a rental: every started hour counts, minimum 1."""
    seconds = (returned_at - datetime.fromisoformat(rented_at)).total_seconds()
    return max(1, math.ceil(seconds / 3600))


def return_vehicle(name, renter=""):
    """Return a rented vehicle to the garage and bill for the time kept."""
    name_key = name.strip().lower()
    for record in rented:
        if _matches_rental(record, name_key, renter):
            rented.remove(record)
            available.append(record["vehicle"])
            hours = _billable_hours(record["timestamp"], datetime.now())
            cost = record["vehicle"].rental_cost(hours)
            print(f"Returned: {record['vehicle']}")
            print(f"Rented at {record['timestamp']}, kept {hours} hour(s)")
            print(f"Amount due: ${cost:,.2f}")
            return record["vehicle"]
    print(f"No rented '{name}' found for {renter or 'anyone'}.")
    return None


def display_availability():
    """Print the full inventory: garage + rented out."""
    if not available and not rented:
        print("The garage is empty.")
        return []
    print(f"In the garage ({len(available)}):")
    for vehicle in available:
        print(f"  {vehicle}")
    if rented:
        print(f"Rented out ({len(rented)}):")
        for record in rented:
            print(
                f"  {record['vehicle']} -> {record['renter']} ({record['timestamp']})"
            )
    return available
