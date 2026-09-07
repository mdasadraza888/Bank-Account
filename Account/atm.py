from account import Account

class Atm():
    def __init__(self, location_id):
        self.location_id = location_id
        self.current_session_account = None
        self.machine_cash_inventory = 100000.0 
