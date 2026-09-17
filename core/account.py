from abc import ABC, abstractmethod
from typing import Self


class Accounts(ABC):
    def __init__(self, account_number=None, account_holder=None, balance=None, pin=None, account_type=None, **kwargs):
        if account_number is None:
            account_number = kwargs.get("account_no")
        if account_holder is None:
            account_holder = kwargs.get("account_holder")
        if balance is None:
            balance = kwargs.get("account_balance")
        if pin is None:
            pin = kwargs.get("account_pin")
        if account_type is None:
            account_type = kwargs.get("account_type", "generic")

        if account_number is None:
            raise ValueError("Account number is required")
        if account_holder is None:
            raise ValueError("Account holder is required")
        if balance is None:
            raise ValueError("Account balance is required")
        if pin is None:
            raise ValueError("PIN is required")

        self.account_number = account_number
        self.account_holder = account_holder
        self.__balance = float(balance)
        self.__account_pin = str(pin)
        self.account_type = account_type

    @abstractmethod
    def withdraw(self, amount, pin):
        pass

    def deposit(self, amount, pin) -> None:
        if pin != self.account_pin:
            raise ValueError("Incorrect PIN")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._change_balance(amount)

    @property
    def account_pin(self) -> str:
        return self.__account_pin

    def get_balance(self) -> float:
        return self.__balance

    def _change_balance(self, amount) -> None:
        self.__balance += amount

    @classmethod
    def create_from_string(cls, account_string) -> Self:
        parts = account_string.split(',')
        if len(parts) == 4:
            account_number, account_holder, balance, pin = parts
            account_type = "generic"
        elif len(parts) >= 5:
            account_number, account_holder, balance, pin, account_type = parts[:5]
        else:
            raise ValueError("String account format must be: account_number,account_holder,balance,pin[,account_type]")

        if cls is not Accounts:
            return cls(
                account_number=account_number,
                account_holder=account_holder,
                balance=float(balance),
                pin=pin,
                account_type=account_type,
            )

        account_type_key = (account_type or "generic").strip().lower()

        if account_type_key.startswith("s"):
            from core.saving_account import SavingAccount
            return SavingAccount(
                account_number=account_number,
                account_holder=account_holder,
                balance=float(balance),
                pin=pin,
                account_type=account_type_key,
            )
        if account_type_key.startswith("b"):
            from core.business_account import BusinessAcoount
            return BusinessAcoount(
                account_number=account_number,
                account_holder=account_holder,
                balance=float(balance),
                pin=pin,
                account_type=account_type_key,
                company_name="Commercial LLC",
            )

        from core.checking_account import CheckingAccount
        return CheckingAccount(
            account_number=account_number,
            account_holder=account_holder,
            balance=float(balance),
            pin=pin,
            account_type=account_type_key or "checking",
        )

    @staticmethod
    def validate_routing_number(routing_number) -> bool:
        if len(routing_number) != 9 or not routing_number.isdigit():
            raise ValueError("Invalid routing number")

        return True