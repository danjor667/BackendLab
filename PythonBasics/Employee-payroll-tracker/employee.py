from abc import ABC, abstractmethod
from utils import format_percent, format_currency


class Employee(ABC):
    """Base class for anyone on the payroll.

    ``tax_rate`` is the stored input (a fraction between 0 and 1); ``salary``,
    ``tax`` and ``net_pay`` are derived values that subclasses compute from
    however they are paid (fixed salary, hourly, stipend, ...).
    """

    def __init__(self, name, base_pay, tax_rate=0.0):
        if base_pay < 0:
            raise ValueError("Pay cannot be negative")
        if not 0.0 <= tax_rate <= 1.0:
            raise ValueError("Tax rate must be between 0 and 1")
        self.name = name
        self._base_pay = base_pay
        self._tax_rate = tax_rate

    @property
    @abstractmethod
    def salary(self):
        """The salary of the employee"""
        raise NotImplementedError(
            "subclasses of Employee must provide their salary implementation"
        )

    @property
    def tax(self):
        """Tax owed on this period's gross pay."""
        return self.salary * self._tax_rate

    @property
    def net_pay(self):
        """Take-home pay after tax."""
        return self.salary - self.tax

    def tax_rate(self):
        """The tax rate of the employee"""
        return self._tax_rate

    def _extra_lines(self):
        """Extra payslip lines for subclasses to override (default: none)."""
        return []

    def generate_payslip(self):
        """Return a formatted payslip for this employee."""
        header = f"Payslip for {self.name} ({type(self).__name__})"
        lines = [
            header,
            "-" * len(header),
        ]
        lines.extend(self._extra_lines())
        lines.extend(
            [
                f"Gross pay:  {format_currency(self.salary)}",
                f"Tax ({format_percent(self._tax_rate)}): {format_currency(self.tax)}",
                f"Net pay:    {format_currency(self.net_pay)}",
            ]
        )
        return "\n".join(lines)


class FullEmployee(Employee):
    """Salaried employee paid a fixed amount each month."""

    def __init__(self, name, annual_salary, tax_rate=0.20):
        super().__init__(name, annual_salary, tax_rate)

    def __str__(self):
        return f"FullEmployee: ({self.name})"

    @property
    def annual_salary(self):
        return self._base_pay

    @property
    def salary(self):
        # Monthly gross pay.
        return self._base_pay / 12

    def _extra_lines(self):
        return [f"Annual salary: {format_currency(self.annual_salary)}"]


class ContractEmployee(Employee):
    """Contractor paid an hourly rate for hours worked in the period."""

    def __init__(self, name, hourly_rate, hours_worked, tax_rate=0.10):
        if hours_worked < 0:
            raise ValueError("Hours worked cannot be negative")
        super().__init__(name, hourly_rate, tax_rate)
        self.hours_worked = hours_worked

    def __str__(self):
        return f"ContractEmployee: ({self.name})"

    @property
    def hourly_rate(self):
        return self._base_pay

    @property
    def salary(self):
        return self._base_pay * self.hours_worked

    def _extra_lines(self):
        return [
            f"Hourly rate: {format_currency(self.hourly_rate)}",
            f"Hours worked: {self.hours_worked}",
        ]


class Intern(Employee):
    """Intern paid a flat monthly stipend, tax-free by default."""

    def __init__(self, name, stipend, tax_rate=0.0):
        super().__init__(name, stipend, tax_rate)

    def __str__(self):
        return f"Intern: ({self.name})"

    @property
    def stipend(self):
        return self._base_pay

    @property
    def salary(self):
        return self._base_pay
