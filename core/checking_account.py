from core.account import Accounts


class CheckingAccount(Accounts):
    def __init__(self, account_number=None, account_holder=None, balance=0.0, pin=None, account_type="checking", overdraft_limit=500.0, **kwargs):
        super().__init__(
            account_number=account_number,
            account_holder=account_holder,
            balance=balance,
            pin=pin if pin is not None else kwargs.get("account_pin"),
            account_type=account_type or kwargs.get("account_type", "checking"),
            **kwargs,
        )
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount, pin) -> str:
        if pin != super().account_pin:
            raise ValueError("Incorrect PIN")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > super().get_balance() + self.overdraft_limit:
            raise ValueError("Insufficient funds, including overdraft limit")

        super()._change_balance(-amount)
        return f"Withdrew ${amount}. Balance: ${super().get_balance()}"
