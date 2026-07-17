# Vehicle Rental System

An interactive command-line rental shop: garage vehicles, rent them out, and bill the renter for the time kept when they come back. Built as an exercise in object-oriented Python: abstract base classes, properties, polymorphic pricing, and a `cmd`-based REPL.

## How it works

The app is a REPL built on Python's standard-library `cmd` module. Commands call helper functions in `utils.py`, which keep two in-memory collections:

- **`available`** — vehicles in the garage, ready to rent
- **`rented`** — active rentals: `{vehicle, renter, timestamp}`

Renting moves a vehicle from the garage to the rental list and stamps the start time. Returning moves it back and **bills for the duration**: every started hour counts (minimum 1 hour), multiplied by the vehicle's hourly rate. On launch the garage is seeded with a few sample vehicles. State is in-memory only — it resets between runs.

### Vehicle ids

Every vehicle gets a short id when it is created: its type's letter plus a per-type counter, so cars are `C1`, `C2`, ..., trucks `T1`, `T2`, ... and bikes `B1`, `B2`, .... `list` shows the id in brackets, and `rent` / `return` take **either an id or a name**:

- An id names exactly one vehicle, so `return T1` is enough — no renter needed.
- A name may hit several vehicles (two different types can both be a "Toyota Corolla"). When it does, the command refuses and prints the candidates so you can repeat it with an id.

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
| `rent <id or name> \| <renter>` | Rent an available vehicle to someone |
| `return <id or name> [\| <renter>]` | Return a vehicle and print the amount due; the renter is only needed to narrow an ambiguous name |
| `list` | Show the full inventory: garage + who has what |
| `quit` (or Ctrl-D) | Exit |

## Example session

```
>> list
In the garage (4):
  [C1] Car 'Toyota Corolla' ($20.00/hour)
  [C2] Car 'Honda Civic' ($22.00/hour)
  [T1] Truck 'Ford F-150' ($60.00/hour)
  [B1] Bike 'Yamaha MT-07' ($9.00/hour)
>> add Vespa Primavera | 12 | bike
Added: [B2] Bike 'Vespa Primavera' ($6.00/hour)
>> rent T1 | Dana
Dana rented [T1] Truck 'Ford F-150' ($60.00/hour)
>> list
In the garage (4):
  [C1] Car 'Toyota Corolla' ($20.00/hour)
  [C2] Car 'Honda Civic' ($22.00/hour)
  [B1] Bike 'Yamaha MT-07' ($9.00/hour)
  [B2] Bike 'Vespa Primavera' ($6.00/hour)
Rented out (1):
  [T1] Truck 'Ford F-150' ($60.00/hour) -> Dana (2026-07-17T06:53:54)
>> return T1
Returned: [T1] Truck 'Ford F-150' ($60.00/hour)
Rented by Dana at 2026-07-17T06:53:54, kept 1 hour(s)
Amount due: $60.00
>> quit
Goodbye.
```

Where a name is ambiguous, the command lists the candidates instead of guessing:

```
>> add Toyota Corolla | 40 | truck
Added: [T2] Truck 'Toyota Corolla' ($60.00/hour)
>> rent Toyota Corolla | Sam
'Toyota Corolla' matches 2 vehicles — use the id instead:
  [C1] Car 'Toyota Corolla' ($20.00/hour)
  [T2] Truck 'Toyota Corolla' ($60.00/hour)
>> rent T2 | Sam
Sam rented [T2] Truck 'Toyota Corolla' ($60.00/hour)
```

## API overview

### `Vehicle` (abstract, `vehicle.py`)

- `Vehicle(name, price)` — validates that the base hourly price is non-negative, then assigns `id`.
- `id` — the vehicle's unique handle, `ID_PREFIX` + a per-type counter (`C1`, `T1`, `B1`, ...).
- `ID_PREFIX` *(class attribute)* — the letter this type's ids start with; defaults to the first letter of the class name.
- `renting_price` *(abstract property)* — effective hourly rate; each subclass derives it from the base price.
- `rental_cost(hours)` — `renting_price × hours`; rejects negative hours.
- Equality (and hashing) is by `id`, so each vehicle is only ever equal to itself.

Each subclass gets its own id counter automatically via `__init_subclass__`, which also rejects a type whose `ID_PREFIX` is already claimed — so a prefix clash is an error at import time rather than confusing ids at runtime.

### Vehicle types

- `Car(name, price)` — ids `C1`, `C2`, ...; rents at the base price.
- `Truck(name, price)` — ids `T1`, `T2`, ...; rents at `price × 1.5` (`Truck.SURCHARGE`).
- `Bike(name, price)` — ids `B1`, `B2`, ...; rents at `price × 0.5` (`Bike.DISCOUNT`).

### Command helpers (`utils.py`)

- `add_vehicle(name, price, kind)` — create the right vehicle type and garage it; rejects same-type duplicate names and invalid prices.
- `rent_vehicle(name_or_id, renter)` — move a vehicle to the rental list with a start timestamp.
- `return_vehicle(name_or_id, renter="")` — move it back, compute billable hours (`ceil` of elapsed time, minimum 1), and print the amount due.
- `display_availability()` — print the garage and active rentals.
- `seed_initial_inventory()` — populate sample vehicles when the garage is empty.

Both `rent_vehicle` and `return_vehicle` resolve their first argument as an id before falling back to a name, and refuse to act on a name that matches more than one vehicle.

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

`Van` needs no `ID_PREFIX` — it defaults to `V`, which nothing else claims, so its vehicles are `V1`, `V2`, .... A type whose first letter is already taken must pick its own, or importing `vehicle.py` fails with a `TypeError` naming the clash:

```python
class Camper(Vehicle):
    """Camper van — 'C' belongs to Car, so claim a free prefix."""

    ID_PREFIX = "M"   # ids M1, M2, ...
```