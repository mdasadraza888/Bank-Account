from account import Account
from datetime import date, time

class BusinessAcoount(Account):
    def __init__(self, account_number, account_holder, balance, pin, company_name):
        super().__init__(account_number, account_holder, balance, pin)
        self.company_name = company_name
        self.transaction_fee = 2.50
        self.daily_withdrawal_limit = 50000.00
        self.total_withdrawan_today = 0
        self.last_date_reset = date.today()

    def withdraw(self, amount, pin):
        self.reset_daily_withdrawal()

        if pin != super().account_pin:
            raise ValueError("Incorrect PIN")
        if amount > super().get_balance():
            print("Insufficient amount")
        if amount < 0:
            print("Amount must be positive")

        
        if self.total_withdrawan_today + amount > self.daily_withdrawal_limit:
            raise ValueError('Declined: Exceed daily withdrawal limit.')

        total_cost = amount + self.transaction_fee
        if total_cost > super().get_balance():
            raise ValueError("Declined: Insufficient funds to cover amount and transaction fee.")

        super()._change_balance(-total_cost)
        self.total_withdrawan_today += amount
        return f"Withdrew ${amount} (fee {self.transaction_fee}). Balance{super().get_balance()}"

    def deposit(self, amount, pin):
        super().deposit(amount, pin)

        self._change_balance(-self.transaction_fee)
        return f"Deposited ${amount}, (Fee: ${self.transaction_fee}, Balance: {self.get_balance()})"

    def reset_daily_withdrawal(self):
        current_date = date.today()

        if current_date != self.last_date_reset:
            self.total_withdrawan_today = 0.0
            self.last_date_reset = current_date

b1 = BusinessAcoount("693258743", "Asad", 10000, "1234", "Apple_plus")
b1.deposit(5000, '1234')
print(b1.get_balance())
b1.withdraw(4000, '1234')
print(b1.get_balance())