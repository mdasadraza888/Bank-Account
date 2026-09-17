import unittest

from core.atm import Atm
from core.checking_account import CheckingAccount
from core.business_account import BusinessAcoount
from core.account import Accounts


class BankAccountTests(unittest.TestCase):
    def test_atm_accepts_machine_api_keywords(self):
        atm = Atm(machine_id="ATM-01", machine_cash_inventory=5000.0)
        self.assertEqual(atm.atm_id, "ATM-01")
        self.assertEqual(atm.machine_cash_inventory, 5000.0)

    def test_checking_account_allows_overdraft_withdrawal(self):
        account = CheckingAccount("1", "Alice", 100.0, "1234", "checking", overdraft_limit=500.0)
        account.withdraw(150.0, "1234")
        self.assertEqual(account.get_balance(), -50.0)

    def test_business_account_handles_deposit_fee(self):
        account = BusinessAcoount("2", "Bob", 5000.0, "4321", "business", "Nexus")
        message = account.deposit(1000.0, "4321")
        self.assertIn("Deposited", message)
        self.assertAlmostEqual(account.get_balance(), 5997.5)

    def test_account_create_from_string_has_required_type(self):
        account = Accounts.create_from_string("3,Carol,250.5,1234,checking")
        self.assertEqual(account.account_holder, "Carol")
        self.assertEqual(account.account_type, "checking")


if __name__ == "__main__":
    unittest.main()
