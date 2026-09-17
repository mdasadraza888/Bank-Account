from core.account import Accounts


class Atm():
    def __init__(self, atm_id=None, initial_amount=50000.00, machine_id=None, machine_cash_inventory=None):
        self.atm_id = atm_id if atm_id is not None else machine_id
        self.machine_cash_inventory = machine_cash_inventory if machine_cash_inventory is not None else initial_amount
        self.current_session_account = None

    def authenticate_user(self, account_obj: Accounts, entered_pin: str) -> bool:
        if account_obj.account_pin == entered_pin:
            self.current_session_account = account_obj
            print(f"Session started for {self.current_session_account}")
            return True

        print("Authentication failed! invalid pin!")
        return False

    def process_withdraw(self, amount: float, pin: str) -> str:
        if not self.current_session_account:
            return "Error, no active card detected."
        if amount > self.machine_cash_inventory:
            return "Transaction Denied: Atm machine has insufficient physical cash"
        if amount < 1:
            return "Amount must be in positive"

        try:
            receipt_msg = self.current_session_account.withdraw(amount=amount, pin=pin)
            self.machine_cash_inventory -= amount
            return f"Dispensing cash... \n{receipt_msg}"
        except ValueError as e:
            return f"Transaction Failed: {str(e)}"