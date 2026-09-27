from core.account import Accounts
from datetime import date


class SavingAccount(Accounts):
    def __init__(self, account_number=None, account_holder=None, balance=0.0, pin=None, account_type="savings", interest_rate=0.04, **kwargs):
        super().__init__(
            account_number=account_number,
            account_holder=account_holder,
            balance=balance,
            pin=pin if pin is not None else kwargs.get("account_pin"),
            account_type=account_type or kwargs.get("account_type", "savings"),
            **kwargs,
        )
        self.interest_rate = interest_rate
        self.withdrawals_this_month = 0
        self.MAX_MONTHLY_WITHDRAWALS = 6
        self.day_of_last_withdrawal = None

    def withdraw(self, amount, pin):
        if pin != super().account_pin:
            raise ValueError("Incorrect PIN")

        self.reset_withdrawals()

        if self.withdrawals_this_month >= self.MAX_MONTHLY_WITHDRAWALS:
            raise ValueError("You have reached the maximum number of withdrawals for this month.")
        if amount > super().get_balance():
            raise ValueError("Insufficient funds")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        super()._change_balance(-amount)
        self.withdrawals_this_month += 1
        self.day_of_last_withdrawal = date.today()
        return f"Withdrew ${amount}. Balance: ${super().get_balance()}"

    def apply_interest(self):
        interest = super().get_balance() * self.interest_rate
        super()._change_balance(interest)
        self.withdrawals_this_month = 0
        return f"Interest applied. Balance: ${super().get_balance()}"

    def reset_withdrawals(self):
        if self.day_of_last_withdrawal is None:
            return
        today = date.today()
        if today.month != self.day_of_last_withdrawal.month:
            self.withdrawals_this_month = 0
            self.day_of_last_withdrawal = None