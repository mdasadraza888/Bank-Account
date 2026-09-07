from account import Account
from datetime import time, date, timedelta

class SavingAccount(Account):
    def __init__(self, account_number, account_holder, balance, pin, interest_rate=0.04):
        super().__init__(account_number, account_holder, balance, pin)
        self.interest_rate = interest_rate
        self.withdrawals_this_month = 0
        self.MAX_MONTHLY_WITHDRAWALS = 6
        self.day_of_last_withdrawal = None

    def withdraw(self, amount, pin):
        if pin != super().account_pin:
            raise ValueError("Incorrect PIN")

        self.reset_withdrawals()

        if self.withdrawals_this_month >= self.MAX_MONTHLY_WITHDRAWALS:
            print("You have reached the maximum number of withdrawals for this month.")
            if self.day_of_last_withdrawal:
                import calendar
                today = date.today()
                _, days_in_month = calendar.monthrange(today.year, today.month)
                remaining_days = days_in_month - today.day
                print(f"Remaining days until withdrawal count reset: {remaining_days} days")

            return
        if amount > super().get_balance():
            raise ValueError("Insufficient funds")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        super()._change_balance(-amount)
        self.withdrawals_this_month += 1
        self.day_of_last_withdrawal = date.today() # Record the date of the last withdrawal

    def apply_interest(self):
        interest = super().get_balance() * self.interest_rate
        super()._change_balance(interest)
        self.withdrawals_this_month = 0 # Reset the withdrawal count after applying interest

    def reset_withdrawals(self):
        if self.day_of_last_withdrawal is None:
            return
        today = date.today()
        if today.month != self.day_of_last_withdrawal.month:
            self.withdrawals_this_month = 0
            self.day_of_last_withdrawal = None # Reset the last withdrawal date after resetting withdrawals
           
saving_account = SavingAccount("987654321", "Jane Doe", 20000, "5678")
saving_account.deposit(1000, "5678")
saving_account.withdraw(500, "5678")
saving_account.withdraw(500, "5678")
saving_account.withdraw(500, "5678")
saving_account.withdraw(500, "5678")
saving_account.withdraw(500, "5678")
saving_account.withdraw(500, "5678")
print(f"Balance after withdrawal: ${saving_account.get_balance()}")

saving_account.withdraw(10000, "5678")
saving_account.withdraw(500, "5678")
print(saving_account.get_balance())