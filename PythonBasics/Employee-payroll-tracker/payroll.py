"""Payroll aggregation: hold a set of employees and total their pay."""
from utils import format_currency

class Payroll:
    def __init__(self):
        self._employees = []

    def add_employee(self, employee):
        self._employees.append(employee)
        return employee

    @property
    def employees(self):
        return tuple(self._employees)

    def total_gross(self):
        return sum(e.salary for e in self._employees)

    def total_tax(self):
        return sum(e.tax for e in self._employees)

    def total_net(self):
        return sum(e.net_pay for e in self._employees)

    def run(self):
        """Print every payslip followed by a summary of the run."""
        for employee in self._employees:
            print(employee.generate_payslip())
            print()
        print(self.summary())

    def summary(self):
        title = f"Payroll summary ({len(self._employees)} employees)"
        return "\n".join([
            title,
            "=" * len(title),
            f"Total gross: {format_currency(self.total_gross())}",
            f"Total tax:   {format_currency(self.total_tax())}",
            f"Total net:   {format_currency(self.total_net())}",
        ])