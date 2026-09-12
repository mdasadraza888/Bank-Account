from fastapi import FastAPI, HTTPException
from Database.db_config import update_account, insert_func, delete_func, get_account, create_account_no
from pydantic import BaseModel

class AccountResponse(BaseModel):
    account_no: int
    account_holder: str
    account_type: str

class AccountRequest(BaseModel):
    account_holder: str
    account_balance: float
    account_pin: str
    account_type: str

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