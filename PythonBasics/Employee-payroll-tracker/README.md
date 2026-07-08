# Employee Payroll Tracker

A small command-line payroll app that models different kinds of employees, computes their pay and tax for a period, and prints individual payslips plus a payroll summary. Built as an exercise in object-oriented Python: abstract base classes, properties, inheritance, and polymorphism.

## How it works

Every employee type inherits from the abstract `Employee` base class and only has to answer one question: *what is your gross pay for the period?* (the `salary` property). Tax, net pay, and payslip formatting are then derived by the base class, so adding a new employee type means writing just a constructor and a `salary` implementation.

```
Employee (ABC)
├── FullEmployee      annual salary / 12 per month, 20% tax by default
├── ContractEmployee  hourly rate × hours worked,   10% tax by default
└── Intern            flat monthly stipend,          0% tax by default
```

The `Payroll` class holds a list of employees and aggregates across them (total gross, total tax, total net). Calling `payroll.run()` prints each employee's payslip followed by the summary.

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
Gross pay:  $7,500.00
Tax (20.0%): $1,500.00
Net pay:    $6,000.00

Payslip for Bob (ContractEmployee)
----------------------------------
Hourly rate: $75.00
Hours worked: 120
Gross pay:  $9,000.00
Tax (10.0%): $900.00
Net pay:    $8,100.00

Payslip for Carol (Intern)
--------------------------
Gross pay:  $2,000.00
Tax (0.0%): $0.00
Net pay:    $2,000.00

Payroll summary (3 employees)
=============================
Total gross: $18,500.00
Total tax:   $2,400.00
Total net:   $16,100.00
```

## API overview

### `Employee` (abstract)

- `Employee(name, base_pay, tax_rate=0.0)` — validates that pay is non-negative and the tax rate is between 0 and 1.
- `salary` *(abstract property)* — gross pay for the period; each subclass defines its own calculation.
- `tax` — `salary * tax_rate`.
- `net_pay` — `salary - tax`.
- `generate_payslip()` — formatted payslip string; subclasses can add extra lines (e.g. hourly rate, annual salary) by overriding `_extra_lines()`.

### Employee types

- `FullEmployee(name, annual_salary, tax_rate=0.20)` — monthly gross pay is `annual_salary / 12`.
- `ContractEmployee(name, hourly_rate, hours_worked, tax_rate=0.10)` — gross pay is `hourly_rate * hours_worked`; rejects negative hours.
- `Intern(name, stipend, tax_rate=0.0)` — gross pay is the flat stipend, tax-free by default.

### `Payroll`

- `add_employee(employee)` — add an employee and return it.
- `employees` — read-only tuple of the current employees.
- `total_gross()` / `total_tax()` / `total_net()` — payroll-wide totals.
- `summary()` — formatted summary string.
- `run()` — print every payslip and the summary.

## Extending

To add a new employee type, subclass `Employee`, pass its pay input as `base_pay` to `super().__init__`, and implement the `salary` property. Override `_extra_lines()` if the payslip should show extra details:

```python
class Manager(Employee):
    def __init__(self, name, annual_salary, bonus, tax_rate=0.25):
        super().__init__(name, annual_salary, tax_rate)
        self.bonus = bonus

    @property
    def salary(self):
        return self._base_pay / 12 + self.bonus

    def _extra_lines(self):
        return [f"Bonus: {format_currency(self.bonus)}"]
```