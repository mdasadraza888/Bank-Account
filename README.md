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

3. ## 💳 Checking Account Module (`CheckingAccount`)

The `CheckingAccount` class manages standard, high-frequency daily spending transactions. It inherits foundational parameters from the core abstract `Account` layout but introduces custom overdraft parameters to handle temporary short-term client debt safely.

### ✨ Key Features & Business Logic
* **Flexible Balance Guardrails:** Unlike savings structures, transactions are not instantly declined if the balance drops to zero. Transactions are permitted to continue processing up into negative values until they hit a predefined financial ceiling.
* **Overdraft Safety Enforcement:** Automatically calculates and verifies if requested withdrawal distributions exceed the combined total of the client's current baseline balance and their allocated credit line.
* **Granular Input Validation:** Requires mandatory double-factor verification via user PIN inputs and restricts transaction execution on invalid (negative/zero) amounts.

### ⚙️ Technical Blueprint

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `overdraft_limit` | `float` | The maximum negative buffer capacity permitted for the client profile (Defaults to `$500.00`). |
| `withdraw(amount, pin)` | `Method` | Overrides the abstract parent signature to validate thresholds and execute line-of-credit deductions. |

### 🚀 Usage Example

```python
from accounts import CheckingAccount

# Initialize a standard daily checking account with a default \$500 overdraft buffer
user_checking = CheckingAccount(
    account_number="CHK-88192", 
    account_holder="Alex Rivera", 
    balance=1200.00, 
    pin="4321"
)

# 1. Standard valid withdrawal
user_checking.withdraw(amount=200.00, pin="4321")
# Output: "Withdrew \$200.00. Balance: \$1000.00"

# 2. Leveraging the overdraft buffer limit
user_checking.withdraw(amount=1300.00, pin="4321")
# Output: "Withdrew \$1300.00. Balance: -\$300.00"

# 3. Transaction blocked for breaching the maximum overdraft ceiling (-\$300 - \$300 exceeds -\$500)
user_checking.withdraw(amount=300.00, pin="4321")
# ValueError: "Insufficient funds (including overdraft)"
```

4. ## 🏢 Business Account Module (`BusinessAccount`)

The `BusinessAccount` class handles large-scale operations for corporate clients. It prioritizes institutional security guardrails and monetization rules, supporting high-volume cash distributions while protecting the bank from commercial fraud through daily spending caps and automated transactional service fees.

### ✨ Key Features & Business Logic
* **Commercial Fee Structure:** Implements a fixed institutional processing fee (e.g., `$2.50`) on both withdrawals and deposits to simulate real-world corporate account management.
* **Daily Anti-Fraud Caps:** Limits financial exposure by tracking total daily asset distribution. Transactions are automatically rejected if the cumulative total exceeds the predefined daily corporate threshold.
* **Self-Healing Date Tracker:** Automatically monitors dates and resets the daily transaction log the moment a new calendar day begins, removing the need for a persistent background resource loop.

### ⚙️ Technical Blueprint

| Attribute / Method | Type | Description |
| :--- | :--- | :--- |
| `company_name` | `string` | The registered corporate legal entity name bound to the profile. |
| `transaction_fee` | `float` | A fixed deduction rate applied to all financial transactions (Defaults to `$2.50`). |
| `daily_withdrawal_limit` | `float` | The maximum cumulative funding cap authorized for 24 hours (Defaults to `$50,000.00`). |
| `withdraw(amount, pin)` | `Method` | Overrides the abstract signature to run dual-factor PIN checks, verify daily capacity, and deduct total transactional costs. |
| `deposit(amount, pin)` | `Method` | Overrides the shared baseline deposit routine to successfully inject assets while applying corporate processing deductions. |

### 🚀 Usage Example

```python
from accounts import BusinessAccount

# Initialize a commercial engine account for a corporate entity
corp_account = BusinessAccount(
    account_number="BUS-77291",
    account_holder="Sarah Jenkins (CFO)",
    balance=100000.00,
    pin="8899",
    company_name="Nexus Tech Solutions LLC"
)

# 1. Processing a business withdrawal (Applies fee: \$2.50)
corp_account.withdraw(amount=5000.00, pin="8899")
# Output: "Withdrew \$5000.00 (Fee: \$2.50). Balance: \$94997.50"

# 2. Corporate deposit with automated processing deductions
corp_account.deposit(amount=10000.00, pin="8899")
# Output: "Deposited \$10000.00 (Fee: \$2.50). Balance: \$104995.00"

# 3. Blocked execution due to crossing the daily corporate safety threshold (\$50k)
corp_account.withdraw(amount=46000.00, pin="8899") 
# ValueError: "Declined: Exceeds daily corporate withdrawal limit" (\$5,000 + \$46,000 > \$50,000)
```
