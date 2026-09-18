from fastapi import APIRouter, HTTPException
from Database.db_config import update_account, insert_func, delete_func, get_account, create_account_no, SessionLocal
from Database.db_models import Account
from pydantic import BaseModel, Field
from core.checking_account import CheckingAccount
from core.saving_account import SavingAccount
from core.business_account import BusinessAcoount
from core.account import Accounts
from typing import Optional
from core.atm import Atm
from enum import Enum

class AccountType(str, Enum):
    checking = "checking"
    savings = "savings"
    business = "business"

class AccountResponse(BaseModel):
    account_no: str
    account_holder: str
    account_type: AccountType

class AccountRequest(BaseModel):
    account_holder: str
    account_balance: float = Field(..., gt=0)
    account_pin: str = Field(..., min_length=4, max_length=4)
    account_type: AccountType

class AccountBusinessRequest(BaseModel):
    account_holder: str
    account_balance: float = Field(..., gt=0)
    account_pin: str = Field(..., min_length=4, max_length=4)
    account_type: AccountType
    company_name: Optional[str] = None


class TransactionRequest(BaseModel):
    account_no: str
    amount: float = Field(..., gt=0.0)
    account_pin: str

class TransactionResponse(BaseModel):
    status: str
    message: str

class AccountUpdateRequest(BaseModel):
    # All field marked optional so the user can choose to change only one element
    account_holder: Optional[str] = Field(None, min_length=2, max_length=50)
    account_pin: Optional[str] = Field(None, min_length=4, max_length=4)

    # custom administrative child fields
    overdraft_value: Optional[float] = None
    company_name: Optional[str] = None
    daily_withdrawal_limit: Optional[float] = None

class AtmWithdrawRequest(BaseModel):
    account_no: str
    entered_pin: str = Field(..., min_length=4, max_length=4)
    amount: float = Field(..., gt=0.0)
    machine_id: str = "ATM-MAIN-BRANCH-01"

class AtmTransactionResponse(BaseModel):
    status: str
    allocated_receipt: str
    updated_balance: float

app = APIRouter(prefix="/accounts", tags=["Banking Ledger Operations"])


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
        "account_no": gen_account_no,
        "account_holder": account.account_holder,
        "account_type": account.account_type
    }

@app.post("/create-business-account", response_model=AccountResponse)
async def create_business_account(account: AccountBusinessRequest) -> AccountResponse:
    gen_account_no = create_account_no()

    db_result = insert_func(
        account_no=gen_account_no,
        account_holder=account.account_holder,
        account_balance=account.account_balance,
        account_pin=account.account_pin,
        account_type=account.account_type,
        company_name=account.company_name
    )

    if db_result.get("status") == 'Error':
        raise HTTPException(status_code=404, detail=db_result.get("message"))

    return {
        "account_no": gen_account_no,
        "account_holder": account.account_holder,
        "account_type": account.account_type
    }

@app.delete("/delete-account/{account_no}")
async def delete_account(account_no: str) -> dict:

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

    if isinstance(result, dict) and result.get("status") == "Error":
        raise HTTPException(status_code=404, detail=result.get("message"))

    return {
        "account_no": result.account_no, 
        "account_holder": result.account_holder,
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

@app.patch("/account/withdraw", response_model=TransactionResponse)
async def process_api_withdrawal(payload: TransactionRequest) -> TransactionResponse:
    session = SessionLocal()
    try:
        db_record = session.query(Account).filter(Account.account_no == payload.account_no).first()

        if not db_record:
            raise HTTPException(status_code=404, detail="Account number not found in our central directory.")

        if db_record.account_type == 'checking':
            active_logic_object=CheckingAccount(
                account_number=db_record.account_no,
                account_holder=db_record.account_holder,
                balance=db_record.account_balance,
                pin=db_record.account_pin,
                account_type=db_record.account_type,
                overdraft_limit=getattr(db_record, 'overdraft_value', 500.00)
            )
        elif db_record.account_type == 'savings':
            active_logic_object=SavingAccount(
                account_number=db_record.account_no,
                account_holder=db_record.account_holder,
                balance=db_record.account_balance,
                pin=db_record.account_pin,
                account_type=db_record.account_type
            )
        elif db_record.account_type == 'business':
            active_logic_object=BusinessAcoount(
                account_number=db_record.account_no,
                account_holder=db_record.account_holder,
                balance=db_record.account_balance,
                pin=db_record.account_pin,
                account_type=db_record.account_type,
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
    except HTTPException:
        session.rollback()
        raise
    except Exception as server_error:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(server_error))
    finally:
        session.close()

@app.patch("/account/deposit/")
async def process_api_deposit(payload: TransactionRequest) -> dict:
    session = SessionLocal()
    try:
        db_account = session.query(Account).filter(Account.account_no == payload.account_no).first()

        if not db_account:
            raise HTTPException(status_code=404, detail="Sorry, Account does not exist.")

        if db_account.account_type == 'business':
            active_logic_object = BusinessAcoount(
                account_number=db_account.account_no,
                account_holder=db_account.account_holder,
                balance=db_account.account_balance,
                pin=db_account.account_pin,
                account_type=db_account.account_type,
                company_name=getattr(db_account, 'company_name', 'Commercial LLC')
            )
        elif db_account.account_type == 'checking':
            active_logic_object = CheckingAccount(
                account_number=db_account.account_no,
                account_holder=db_account.account_holder,
                balance=db_account.account_balance,
                pin=db_account.account_pin,
                account_type=db_account.account_type,
                overdraft_limit=getattr(db_account, 'overdraft_value', 500.00)
            )
        elif db_account.account_type == 'savings':
            active_logic_object = SavingAccount(
                account_number=db_account.account_no,
                account_holder=db_account.account_holder,
                balance=db_account.account_balance,
                pin=db_account.account_pin,
                account_type=db_account.account_type,
            )
        else:
            raise HTTPException(status_code=404, detail="Unsupported polymorphic account type.")

        success_message = active_logic_object.deposit(amount=payload.amount, pin=payload.account_pin)

        db_account.account_balance = active_logic_object.get_balance()
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

@app.get("/account/{account_no}/balance")
async def retrieve_account_balance(account_no: str) -> dict:

    db_account = get_account(account_no=account_no)

    if not db_account:
        raise HTTPException(status_code=404, detail="Account not founded.")

    return {'status': "success", "message": f"Balance: {db_account.account_balance}"}


@app.post("/ATM/withdraw", response_model=AtmTransactionResponse)
async def withdraw_money(payload: AtmWithdrawRequest) -> AtmTransactionResponse:
    session = SessionLocal()
    hardware_atm = None
    try:
        db_account = session.query(Account).filter(
            Account.account_no == payload.account_no
        ).first()

        if not db_account:
            raise HTTPException(status_code=404, detail="Account does not exist")

        hardware_atm = Atm(atm_id=payload.machine_id, machine_cash_inventory=50000.00)

        is_authenticate = hardware_atm.authenticate_user(account_obj=db_account, entered_pin=payload.entered_pin)

        if not is_authenticate:
            raise HTTPException(status_code=404, detail="ATM Error: Access Denied. Invalid PIN entry")

        if db_account.account_type == 'checking':
            active_account_logic = CheckingAccount(
                account_number=db_account.account_no,
                account_holder=db_account.account_holder,
                balance=db_account.account_balance,
                pin=db_account.account_pin,
                account_type=db_account.account_type,
                overdraft_limit=getattr(db_account, 'overdraft_value', 500.00)
            )
        elif db_account.account_type == 'savings':
            active_account_logic = SavingAccount(
                account_number=db_account.account_no,
                account_holder=db_account.account_holder,
                balance=db_account.account_balance,
                pin=db_account.account_pin,
                account_type=db_account.account_type,
            )
        elif db_account.account_type == 'business':
            active_account_logic = BusinessAcoount(
                account_number=db_account.account_no,
                account_holder=db_account.account_holder,
                balance=db_account.account_balance,
                pin=db_account.account_pin,
                account_type=db_account.account_type,
                company_name=getattr(db_account, 'company_name', 'Commercial LLC')
            )
        else:
            raise HTTPException(status_code=404, detail="ATM Error: unrecognized card allocation schema.")

        hardware_atm.current_session_account = active_account_logic
        receipt_msg = hardware_atm.process_withdraw(amount=payload.amount, pin=payload.entered_pin)

        if 'Failed' in receipt_msg:
            raise HTTPException(status_code=404, detail=receipt_msg)

        db_account.account_balance = active_account_logic.get_balance()
        session.commit()
        session.refresh(db_account)

        return {
            "status": "success",
            "allocated_receipt": f"Thank you for using our ATM network. {receipt_msg}",
            "updated_balance": active_account_logic.get_balance()
        }
    except ValueError as domain_error:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(domain_error))
    except HTTPException:
        session.rollback()
        raise
    except Exception as server_error:
        session.rollback()
        raise HTTPException(status_code=404, detail=f"Internal ledger crash: {str(server_error)}")
    finally:
        if hardware_atm is not None:
            hardware_atm.logout()
        session.close()
