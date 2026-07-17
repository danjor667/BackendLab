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


def _all_vehicles():
    """Every vehicle the shop owns, garaged or out on rental."""
    return [*available, *(record["vehicle"] for record in rented)]


def _find_duplicate(cls, name):
    """The vehicle of the same type and name already owned, if any."""
    key = name.lower()
    for vehicle in _all_vehicles():
        if type(vehicle) is cls and vehicle.name.lower() == key:
            return vehicle
    return None


def add_vehicle(name, price, kind="car"):
    """Create and garage a vehicle. Returns it, or None if it already exists."""
    cls = _VEHICLE_KINDS.get(kind.lower(), Car)
    if isinstance(price, str):
        try:
            price = float(price)
        except ValueError:
            print(f"Invalid price: '{price}'")
            return None
    name = name.strip()
    existing = _find_duplicate(cls, name)
    if existing is not None:
        print(f"Already in the garage: {existing}")
        return None
    vehicle = cls(name, price)
    available.append(vehicle)
    print(f"Added: {vehicle}")
    return vehicle


def _lookup(vehicles, key):
    """Vehicles matching `key`, which may be an id or a name.

    Ids are unique, so an id hit is always a single vehicle and wins outright;
    names can collide across types, so a name hit may return several.
    """
    key = key.strip().lower()
    by_id = [v for v in vehicles if v.id.lower() == key]
    if by_id:
        return by_id
    return [v for v in vehicles if v.name.lower() == key]


def _report_ambiguous(key, lines):
    """Tell the user their key hit several vehicles and to use an id instead."""
    print(f"'{key}' matches {len(lines)} vehicles — use the id instead:")
    for line in lines:
        print(f"  {line}")


def rent_vehicle(name_or_id, renter):
    """Move a vehicle from the garage to a renter, found by id or name."""
    matches = _lookup(available, name_or_id)
    if not matches:
        print(f"Not available to rent: '{name_or_id}'")
        return None
    if len(matches) > 1:
        _report_ambiguous(name_or_id, [str(v) for v in matches])
        return None
    vehicle = matches[0]
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


def _billable_hours(rented_at, returned_at):
    """Hours to bill for a rental: every started hour counts, minimum 1."""
    seconds = (returned_at - datetime.fromisoformat(rented_at)).total_seconds()
    return max(1, math.ceil(seconds / 3600))


def return_vehicle(name_or_id, renter=""):
    """Return a rented vehicle to the garage and bill for the time kept.

    The vehicle is found by id or by name; an id identifies the rental on its
    own, so `renter` is only needed to narrow an ambiguous name.
    """
    matches = _lookup([r["vehicle"] for r in rented], name_or_id)
    records = [r for r in rented if r["vehicle"] in matches]
    if renter:
        records = [r for r in records if r["renter"].lower() == renter.lower()]
    if not records:
        print(f"No rented '{name_or_id}' found for {renter or 'anyone'}.")
        return None
    if len(records) > 1:
        _report_ambiguous(
            name_or_id, [f"{r['vehicle']} -> {r['renter']}" for r in records]
        )
        return None
    record = records[0]
    rented.remove(record)
    available.append(record["vehicle"])
    hours = _billable_hours(record["timestamp"], datetime.now())
    cost = record["vehicle"].rental_cost(hours)
    print(f"Returned: {record['vehicle']}")
    print(f"Rented by {record['renter']} at {record['timestamp']}, kept {hours} hour(s)")
    print(f"Amount due: ${cost:,.2f}")
    return record["vehicle"]


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
