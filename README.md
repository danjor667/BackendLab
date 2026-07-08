# BackendLab

Hands-on labs for my Python backend specialisation. Each lab is a small, self-contained project built to practice a set of backend concepts — every one has its own README with the details.

## Labs

### PythonBasics

Object-oriented Python fundamentals: abstract base classes, inheritance, properties, polymorphism, serialization, and file persistence.

| Lab | What it is | Concepts |
| --- | --- | --- |
| [Employee Payroll Tracker](PythonBasics/Employee-payroll-tracker/README.md) | Computes pay and tax per employee type and prints payslips | ABCs, abstract properties, inheritance |
| [Library Inventory](PythonBasics/Library-Inventory/README.md) | Interactive CLI to shelve, search, borrow, and return books | Polymorphic JSON serialization, file persistence, `cmd` REPL |
| [Vehicle Rental System](PythonBasics/Vehicle-rental-system/README.md) | Interactive CLI to rent out vehicles and bill by time kept | Polymorphic pricing, duration-based billing, `cmd` REPL |

More sections will be added as the specialisation progresses.

## Running a lab

Each lab runs standalone on Python 3.11+ with no external dependencies:

```bash
cd PythonBasics/<lab-name>
python main.py
```
