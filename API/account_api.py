from fastapi import FastAPI, HTTPException
from Database.db_config import update_account, insert_func, delete_func, get_account, create_account_no, SessionLocal
from Database.db_models import Account
from pydantic import BaseModel
from core.checking_account import CheckingAccount
from core.saving_account import SavingAccount
from core.business_account import BusinessAcoount


class AccountResponse(BaseModel):
    account_no: int
    account_holder: str
    account_type: str

class AccountRequest(BaseModel):
    account_holder: str
    account_balance: float
    account_pin: str
    account_type: str

class TransactionRequest(BaseModel):
    account_no: str
    amount: float
    account_pin: str


app = FastAPI()


@app.post("/account", response_model=AccountResponse)
async def create_account(account: AccountRequest):
    gen_account_no = create_account_no()

    db_result = insert_func(
        account_no=gen_account_no, 
        account_holder=account.account_holder, 
        account_balance=account.account_balance, 
        account_pin=account.account_pin, 
        account_type=account.account_type
    )

    if db_result.get("status") == "Error":
        raise HTTPException(status_code=404, detail=db_result.get("message"))

    return {
        "account_no": gen_account_no,
        "account_holder": account.account_holder,
        "account_type": account.account_type
    }

@app.get("/account/withdraw")
async def process_api_withdrawal(payload: TransactionRequest):
    session = SessionLocal()
    try:
        db_record = session.query(Account).filter(Account.account_no == payload.account_no).first()

        if not db_record:
            raise HTTPException(status_code=404, detail="Account number not found in our central directory.")

        if db_record.account_type == 'checking':
            active_logic_object=Account(
                account_no = db_record.account_no,
                account_holder=db_record.account_holder,
                account_balance=db_record.account_balance,
                account_pin=db_record.account_pin,
                overdraft_limit=getattr(db_record, 'overdraft_value', 500.00)
            )
        elif db_record.account_type == 'savings':
            active_logic_object=SavingAccount(
                account_no=db_record.account_no,
                account_holder=db_record.account_holder,
                account_balance=db_record.account_balance,
                account_pin=db_record.account_pin,
            )
        elif db_record.account_type == 'business':
            active_logic_object=BusinessAcoount(
                account_no=db_record.account_no,
                account_holder=db_record.account_holder,
                account_balance=db_record.account_balance,
                account_pin=db_record.account_pin,
                company_name=getattr(db_record, 'company_name', 'Commercial LLC')
            )
        else:
            raise HTTPException(status_code=404, detail="Unsupported polymorphic account type.")

        success_message = active_logic_object.withdraw(payload.amount, payload.account_pin)

        db_record.account_balance = active_logic_object.get_balance()
        
    finally:
        pass