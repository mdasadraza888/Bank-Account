from account import Accounts
from business_account import BusinessAcoount
from checking_account import CheckingAccount
from saving_account import SavingAccount


class Atm():
    def __init__(self, atm_id, location_id):
        self.atm_id = atm_id
        self.location_id = location_id
        self.current_session_account = None
        self.machine_cash_inventory = 100000.0 





