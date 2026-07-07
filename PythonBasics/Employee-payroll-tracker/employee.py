from abc import ABC, abstractmethod

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


    @abstractmethod
    @property
    def salary(self):
        """The salary of the employee"""
        raise NotImplementedError("subclasses of Employee must provide their salary implementation")


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



    def generate_payslip(self):
        pass






class FullEmployee(Employee):
    pass



class ContractEmployee(Employee):
    pass



class Intern(Employee):
    pass
