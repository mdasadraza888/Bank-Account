from fastapi import FastAPI, HTTPException
from Database.db_config import update_account, insert_func, delete_func, get_account, create_account_no, SessionLocal
from Database.db_models import Account
from pydantic import BaseModel, Field
from core.checking_account import CheckingAccount
from core.saving_account import SavingAccount
from core.business_account import BusinessAcoount
from core.account import Accounts
from typing import Optional


class AccountResponse(BaseModel):
    account_no: str
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

class AccountUpdateRequest(BaseModel):
    # All field marked optional so the user can choose to change only one element
    account_holder: Optional[str] = Field(None, min_length=2, max_length=50)
    account_pin: Optional[str] = Field(None, min_length=4, max_length=4)

    # custom administrative child fields
    overdraft_value: Optional[float] = None
    company_name: Optional[str] = None
    daily_withdrawal_limit: Optional[float] = None


app = FastAPI()


@app.post("/create-account", response_model=AccountResponse)
async def create_account(account: AccountRequest) -> AccountResponse:
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
        "account_no": int(gen_account_no),
        "account_holder": account.account_holder,
        "account_type": account.account_type
    }

@app.delete("/delete-account/{account_no}")
async def delete_account(account_no: str) -> str:

    result = delete_func(account_no=account_no)

    if result.get('status') == 'Error':
        raise HTTPException(status_code=404, detail=result.get("message"))

    return {"status": "success", "message": result.get("message")}

@app.patch("/update-account/{account_no}", response_model=AccountResponse)
async def modify_account_profile(account_no: str, payload: AccountUpdateRequest) -> AccountResponse:

    clean_data = payload.model_dump(exclude_unset=True)

    if not clean_data:
        raise HTTPException(status_code=404, detail="No valid updates attributed were supplied!")

    result = update_account(account_no=account_no, updated_data=clean_data)

    if result.get("status") == "Error":
        raise HTTPException(status_code=404, detail=result.get("message"))

    return {
        "account_no": result.account_no, 
        "account_holder": payload.account_holder,
        "account_type": result.account_type
    }

@app.get("/account/{account_no}", response_model=AccountResponse)
async def get_account_profile(account_no: str) -> AccountResponse:

    account = get_account(account_no=account_no)

    if not account:
        raise HTTPException(status_code=404, detail="Sorry Account no not found.")

    return {
        "account_no": account.account_no,
        "account_holder": account.account_holder,
        "account_type": account.account_type
    }

@app.patch("/account/withdraw/{account_no}")
async def process_api_withdrawal(payload: TransactionRequest) -> str:
    session = SessionLocal()
    try:
        db_record = session.query(Account).filter(Account.account_no == payload.account_no).first()

        if not db_record:
            raise HTTPException(status_code=404, detail="Account number not found in our central directory.")

        if db_record.account_type == 'checking':
            active_logic_object=CheckingAccount(
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
        session.commit()

        return {"status": "success", "message": success_message}
    except ValueError as domain_error:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(domain_error))
    except Exception as server_error:
        session.rollback()
        raise HTTPException(status_code=404, detail=f"Internal server error {str(server_error)}")
    finally:
        session.close()

@app.patch("/account/deposit/{account_no}")
async def process_api_deposit(payload: TransactionRequest) -> str:
    session = SessionLocal()
    try:
        db_account = session.query(Account).filter(Account.account_no == payload.account_no).first()

        if not db_account:
            raise HTTPException(status_code=404, detail="Sorry, Account does not exist.")

        if db_account.account_type == 'business':
            active_logic_object=BusinessAcoount(
                account_no=db_account.account_no,
                account_holder=db_account.account_holder,
                account_balance=db_account.account_balance,
                account_pin=db_account.account_pin,
                company_name=getattr(db_account, 'company_name', 'Commercial LLC')
            )
        elif db_account.account_type in ('checking', 'savings'):
            active_logic_object=Account(
                account_no=db_account.account_no,
                account_holder=db_account.account_holder,
                account_balance=db_account.account_balance,
                account_pin=db_account.account_pin,
                account_type=db_account.account_type
            )
        else:
            raise HTTPException(status_code=404, detail="Unsupported polymorphic account type.")

        success_message = active_logic_object.deposit(amount=payload.amount, pin=payload.account_pin) # it works on backend logic

        db_account.account_balance = active_logic_object.get_balance() # it change balance into database
        session.commit()

        return {'status': 'success', 'message': success_message}
    except ValueError as domain_error:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(domain_error))
    except Exception as server_error:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(server_error))
    finally:
        session.close()