# Employee Payroll Tracker

A small command-line payroll app that models different kinds of employees, computes their pay and tax for a period, and prints individual payslips plus a payroll summary. Built as an exercise in object-oriented Python: abstract base classes, properties, inheritance, and polymorphism.

## How it works

Every employee type inherits from the abstract `Employee` base class and only has to answer one question: *what is your regular pay for the period?* (the `base_salary` property). Gross pay, tax, net pay, and payslip formatting are then derived by the base class, so adding a new employee type means writing just a constructor and a `base_salary` implementation.

A type may also override `bonus` to earn one; the base class returns `0.0`, so a bonus is opt-in. Bonuses are treated as taxable income — gross pay is `base_salary + bonus`, and tax applies to that total.

```
Employee (ABC)
├── FullEmployee      annual salary / 12 per month, 20% tax by default
│                     bonus: 10% of monthly pay
├── ContractEmployee  hourly rate × hours worked,   10% tax by default
│                     bonus: overtime premium — hours past 100 at 0.5× rate
└── Intern            flat monthly stipend,          0% tax by default
                      bonus: flat $250 completion bonus
```

The `Payroll` class holds a list of employees and aggregates across them (total base, bonus, gross, tax, net). Calling `payroll.run()` prints each employee's payslip followed by the summary.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Entry point — builds a sample payroll and runs it |
| `employee.py` | `Employee` abstract base class and the three concrete employee types |
| `payroll.py` | `Payroll` aggregator: holds employees, totals pay, prints the report |
| `utils.py` | Formatting helpers (`format_currency`, `format_percent`) |

## Requirements

- Python 3.11+
- No runtime dependencies (Poetry is used for project management; `black` is a dev tool)

## Running

```bash
cd PythonBasics/Employee-payroll-tracker
python main.py
```

Or with Poetry:

```bash
poetry install
poetry run python main.py
```

## Example output

```
Payslip for Alice (FullEmployee)
--------------------------------
Annual salary: $90,000.00
Base pay:   $7,500.00
Bonus:      $750.00
Gross pay:  $8,250.00
Tax (20.0%): $1,650.00
Net pay:    $6,600.00

Payslip for Bob (ContractEmployee)
----------------------------------
Hourly rate: $75.00
Hours worked: 120
Base pay:   $9,000.00
Bonus:      $750.00
Gross pay:  $9,750.00
Tax (10.0%): $975.00
Net pay:    $8,775.00

Payslip for Carol (Intern)
--------------------------
Base pay:   $2,000.00
Bonus:      $250.00
Gross pay:  $2,250.00
Tax (0.0%): $0.00
Net pay:    $2,250.00

Payroll summary (3 employees)
=============================
Total base:  $18,500.00
Total bonus: $1,750.00
Total gross: $20,250.00
Total tax:   $2,625.00
Total net:   $17,625.00
```

## API overview

### `Employee` (abstract)

- `Employee(name, base_pay, tax_rate=0.0)` — validates that pay is non-negative and the tax rate is between 0 and 1.
- `base_salary` *(abstract property)* — regular pay for the period, before bonus; each subclass defines its own calculation.
- `bonus` — bonus earned this period. Returns `0.0` unless a subclass overrides it.
- `salary` — gross pay: `base_salary + bonus`.
- `tax` — `salary * tax_rate`, so bonuses are taxed alongside regular pay.
- `net_pay` — `salary - tax`.
- `generate_payslip()` — formatted payslip string; subclasses can add extra lines (e.g. hourly rate, annual salary) by overriding `_extra_lines()`.

### Employee types

- `FullEmployee(name, annual_salary, tax_rate=0.20)` — regular pay is `annual_salary / 12`. Bonus is `BONUS_RATE` (10%) of that.
- `ContractEmployee(name, hourly_rate, hours_worked, tax_rate=0.10)` — regular pay is `hourly_rate * hours_worked`; rejects negative hours. Bonus is an overtime premium: hours beyond `OVERTIME_AFTER` (100) earn an extra `OVERTIME_PREMIUM` (0.5) × the hourly rate, and no overtime means no bonus.
- `Intern(name, stipend, tax_rate=0.0)` — regular pay is the flat stipend, tax-free by default. Bonus is a flat `COMPLETION_BONUS` ($250).

Each rule is tuned by the class constants above, so changing a bonus policy is a one-line edit rather than a code change.

### `Payroll`

- `add_employee(employee)` — add an employee and return it.
- `employees` — read-only tuple of the current employees.
- `total_base()` / `total_bonus()` / `total_gross()` / `total_tax()` / `total_net()` — payroll-wide totals.
- `summary()` — formatted summary string.
- `run()` — print every payslip and the summary.

## Extending

To add a new employee type, subclass `Employee`, pass its pay input as `base_pay` to `super().__init__`, and implement the `base_salary` property. Override `bonus` if the type earns one, and `_extra_lines()` if the payslip should show extra details:

```python
class Manager(Employee):
    """Salaried manager who also earns a bonus per direct report."""

    BONUS_PER_REPORT = 200.0

    def __init__(self, name, annual_salary, reports, tax_rate=0.25):
        super().__init__(name, annual_salary, tax_rate)
        self.reports = reports

    @property
    def base_salary(self):
        return self._base_pay / 12

    @property
    def bonus(self):
        return self.reports * self.BONUS_PER_REPORT

    def _extra_lines(self):
        return [f"Direct reports: {self.reports}"]
```

The base class handles the rest: `salary` becomes `base_salary + bonus`, tax applies to that total, and `Payroll` picks the new type up in its totals with no changes.