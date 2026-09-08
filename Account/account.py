from abc import ABC, abstractmethod

class Account(ABC):
    def __init__(self, account_number, account_holder, balance, pin, account_type):
        self.account_number = account_number
        self.account_holder = account_holder
        self.__balance = balance
        self.__account_pin = pin
        self.account_type = account_type
        
    @abstractmethod
    def withdraw(self, amount, pin):
        pass
    
    def deposit(self, amount, pin):
        if pin != self.account_pin:
            raise ValueError("Incorrect PIN")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._change_balance(amount)

    @property
    def account_pin(self):
        return self.__account_pin

    def get_balance(self):
        return self.__balance

    def _change_balance(self, amount):
        self.__balance += amount

    @classmethod
    def create_from_string(cls, account_string):
        account_number, account_holder, balance, pin = account_string.split(',')
        return cls(account_number, account_holder, float(balance), pin)

    @staticmethod
    def validate_routing_number(routing_number):
        # Implement routing number validation logic here
        if len(routing_number) != 9 or not routing_number.isdigit():
            raise ValueError("Invalid routing number")

        return True