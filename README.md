# Bank-Account
This is a bank that manage account of customers
1. ### Base Account Component

The Account class serves as the foundational building block for all bank account variations (e.g., SavingAccount). It provides core encapsulation for sensitive data like PINs and account balances, exposing secure methods for day-to-day banking transactions. 

### Key Features

* **Encapsulation:** Secures the account's internal state, protecting the balance and PIN from unauthorized external modifications.
* **Basic Ledger Actions:** Standardized logic for checking balances, processing deposits, and authenticating user actions.
* **Extensibility:** Built with hooks (like _change_balance) allowing subclasses to easily build advanced features on top of core transaction mechanics.

### Method Specifications

Method / Property 

Access 

Description 

**get_balance()**
PublicSafely retrieves the current account balance.
**deposit(amount)**
PublicValidates and adds a positive cash amount to the balance.
**account_pin**
PropertyExposes the account PIN securely for subclass authentication validation.
**_change_balance(amount)**
ProtectedInternal method allowing subclasses to alter balances directly during adjustments like interest or penalties.

### Quick Start Example

python

from account import Account

# Initialize a standard bank account
base_account = Account(
    account_number="123456789", 
    account_holder="John Doe", 
    balance=5000, 
    pin="1234"
)

# Deposit funds
base_account.deposit(1500)

# Check balance
print(f"Current Balance: ${base_account.get_balance()}") # Outputs: $6500

Use code with caution.

2. ### Savings Account Component

The SavingAccount class extends the base Account class to implement a high-yield savings system. It includes automated monthly withdrawal limitations to mimic real-world banking regulations, and an interest capitalization mechanism. 

### Key Features

* **Interest Accrual:** Apply a customizable annual interest rate (defaults to 4%) directly to the account balance using the apply_interest() method.
* **Automated Regulatory Caps:** Restricts users to a maximum of 6 withdrawals per calendar month to comply with standard banking policies.
* **Smart Calendar Tracking:** Dynamically computes calendar month lengths (accounting for 28, 30, and 31-day months) to inform users exactly how many days remain before their withdrawal limit resets.
* **Zero-Touch Reset Engine:** Automatically detects when a new calendar month or year has started on the user's next transaction, instantly clearing their withdrawal history without requiring manual cron jobs.

### Method Specifications

Method 

Description 

**withdraw(amount, pin)**
Processes a withdrawal if the PIN matches, funds are sufficient, and the monthly limit (6) hasn't been breached.
**apply_interest()**
Multiplies the current balance by the interest rate and adds the earnings back into the account.
**reset_withdrawals()**
Internal check that resets the monthly withdrawal counters seamlessly if the system detects a change in the calendar month or year.

### Quick Start Example

python

from datetime import date
from saving_account import SavingAccount

# Initialize an account with a 4% default interest rate
account = SavingAccount(
    account_number="987654321", 
    account_holder="Jane Doe", 
    balance=20000, 
    pin="5678"
)

# Make a withdrawal
account.withdraw(500, "5678")

# Capitalize monthly interest earnings
account.apply_interest()

Use code with caution.