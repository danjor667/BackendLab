# Vehicle Rental System

An interactive command-line rental shop: garage vehicles, rent them out, and bill the renter for the time kept when they come back. Built as an exercise in object-oriented Python: abstract base classes, properties, polymorphic pricing, and a `cmd`-based REPL.

## How it works

The app is a REPL built on Python's standard-library `cmd` module. Commands call helper functions in `utils.py`, which keep two in-memory collections:

- **`available`** — vehicles in the garage, ready to rent
- **`rented`** — active rentals: `{vehicle, renter, timestamp}`

Renting moves a vehicle from the garage to the rental list and stamps the start time. Returning moves it back and **bills for the duration**: every started hour counts (minimum 1 hour), multiplied by the vehicle's hourly rate. On launch the garage is seeded with a few sample vehicles. State is in-memory only — it resets between runs.

### Pricing model

`Vehicle` is an abstract base class that stores the base hourly price and requires each subclass to define `renting_price` — the effective hourly rate derived from it:

```
Vehicle (ABC)
├── Car     base price as-is
├── Truck   base price × 1.5  (heavy-vehicle surcharge)
└── Bike    base price × 0.5  (two-wheeler discount)
```

So a truck garaged at a base price of 40 rents at $60.00/hour, while a bike at 18 rents at $9.00/hour. `rental_cost(hours)` on the base class turns that rate into a total bill.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Entry point — the `Console` REPL (built on `cmd.Cmd`) that parses commands |
| `vehicle.py` | `Vehicle` ABC and the `Car` / `Truck` / `Bike` types with their pricing |
| `utils.py` | Command implementations: add, rent, return (with billing), list, seed |

## Requirements

- Python 3.11+ (standard library only, no dependencies)

## Running

```bash
cd PythonBasics/Vehicle-rental-system
python main.py
```

## Commands

Arguments with multiple fields are separated by a pipe (`|`):

| Command | Description |
| --- | --- |
| `add <name> \| <hourly price> [\| car\|truck\|bike]` | Garage a new vehicle (kind defaults to `car`) |
| `rent <name> \| <renter>` | Rent an available vehicle to someone |
| `return <name> [\| <renter>]` | Return a vehicle and print the amount due; renter narrows the match |
| `list` | Show the full inventory: garage + who has what |
| `quit` (or Ctrl-D) | Exit |

## Example session

```
>> list
In the garage (4):
  Car 'Toyota Corolla' ($20.00/hour)
  Car 'Honda Civic' ($22.00/hour)
  Truck 'Ford F-150' ($60.00/hour)
  Bike 'Yamaha MT-07' ($9.00/hour)
>> add Vespa Primavera | 12 | bike
Added: Bike 'Vespa Primavera' ($6.00/hour)
>> rent Ford F-150 | Dana
Dana rented Truck 'Ford F-150' ($60.00/hour)
>> list
In the garage (4):
  Car 'Toyota Corolla' ($20.00/hour)
  Car 'Honda Civic' ($22.00/hour)
  Bike 'Yamaha MT-07' ($9.00/hour)
  Bike 'Vespa Primavera' ($6.00/hour)
Rented out (1):
  Truck 'Ford F-150' ($60.00/hour) -> Dana (2026-07-08T10:57:06)
>> return Ford F-150 | Dana
Returned: Truck 'Ford F-150' ($60.00/hour)
Rented at 2026-07-08T10:57:06, kept 1 hour(s)
Amount due: $60.00
>> quit
Goodbye.
```

## API overview

### `Vehicle` (abstract, `vehicle.py`)

- `Vehicle(name, price)` — validates that the base hourly price is non-negative.
- `renting_price` *(abstract property)* — effective hourly rate; each subclass derives it from the base price.
- `rental_cost(hours)` — `renting_price × hours`; rejects negative hours.
- Equality is same type + case-insensitive name, used for duplicate detection.

### Vehicle types

- `Car(name, price)` — rents at the base price.
- `Truck(name, price)` — rents at `price × 1.5` (`Truck.SURCHARGE`).
- `Bike(name, price)` — rents at `price × 0.5` (`Bike.DISCOUNT`).

### Command helpers (`utils.py`)

- `add_vehicle(name, price, kind)` — create the right vehicle type and garage it; rejects duplicates and invalid prices.
- `rent_vehicle(name, renter)` — move a vehicle to the rental list with a start timestamp.
- `return_vehicle(name, renter="")` — move it back, compute billable hours (`ceil` of elapsed time, minimum 1), and print the amount due.
- `display_availability()` — print the garage and active rentals.
- `seed_initial_inventory()` — populate sample vehicles when the garage is empty.

## Extending

To add a new vehicle type, subclass `Vehicle`, implement the `renting_price` property, and add the class to the `VEHICLE_TYPES` tuple in `vehicle.py` — the `add` command resolves kinds by lowercase class name, so `add Camper One | 30 | van` works as soon as `Van` is registered:

```python
class Van(Vehicle):
    """Passenger van, rented with a 25% surcharge."""

    @property
    def renting_price(self):
        return self._base_price * 1.25

VEHICLE_TYPES = (Car, Truck, Bike, Van)
```