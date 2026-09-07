from account import Account

class CheckingAccount(Account):
    def __init__(self, account_number, account_holder, balance, pin, overdraft_limit=500):
        super().__init__(account_number, account_holder, balance, pin)
        self.overdraft_limit = overdraft_limit


    def withdraw(self, amount, pin):
        if pin != super().account_pin:
            raise ValueError("Incorrect PIN")
        if amount > super().get_balance() + self.overdraft_limit:
            raise ValueError("Insufficient funds, including overdraft limit")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        super()._change_balance(-amount)

    

my_account = CheckingAccount("123456789", "John Doe", 1000, "1234")
print(f"Initial balance: ${my_account.get_balance()}")
my_account.deposit(500, "1234")
print(f"Balance after deposit: ${my_account.get_balance()}")
my_account.withdraw(200, "1234")
print(f"Balance after withdrawal: ${my_account.get_balance()}")
