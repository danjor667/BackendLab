"""
main entry point of the app
"""

from payroll import Payroll
from employee import FullEmployee, ContractEmployee, Intern


def main():
    payroll = Payroll()
    payroll.add_employee(FullEmployee("Alice", annual_salary=90000))
    payroll.add_employee(ContractEmployee("Bob", hourly_rate=75, hours_worked=120))
    payroll.add_employee(Intern("Carol", stipend=2000))

    payroll.run()


if __name__ == "__main__":
    main()
