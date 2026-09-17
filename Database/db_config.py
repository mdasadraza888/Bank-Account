from sqlalchemy import create_engine, insert, update, delete, select
from sqlalchemy.orm import sessionmaker
from Database.db_models import Base, Account, SavingAccount, CheckingAccount, BusinessAccount
import random

engine = create_engine("postgresql://postgres:asad888@127.0.0.1:5432/Bank Account")

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def insert_func(account_no: str, account_holder: str, account_balance: float, account_pin: str, account_type: str, company_name: str):
    session = SessionLocal()

    target_type = account_type.strip().lower()
    try:
        if target_type.startswith('s'):
            new_account = SavingAccount(
                account_no = str(account_no).strip(),
                account_holder = account_holder,
                account_balance = float(account_balance),
                account_pin = account_pin,
                account_type = account_type
            )
        elif target_type.startswith('c'):
            new_account = CheckingAccount(
                account_no = str(account_no).strip(),
                account_holder = account_holder,
                account_balance = float(account_balance),
                account_pin = account_pin,
                account_type = account_type
            )
        elif target_type.startswith('b'):
            new_account = BusinessAccount(
                account_no = str(account_no).strip(),
                account_holder = account_holder,
                account_balance = float(account_balance),
                account_pin = account_pin,
                account_type = account_type,
                company_name = company_name
            )
        else:
            raise ValueError(f"Account type category '{account_type} is unsporrted.")

        session.add(new_account)
        session.commit()
        session.refresh(new_account)

        return {'status': 'Success', "message": f"Your {target_type} has been created with ID: {new_account.account_id}"}
    except Exception as e:
        session.rollback()
        return {'status': 'Error', "message": f"Database execution failed: {str(e)}"}
    finally:
        session.close()


def delete_func(account_no: str):
    session = SessionLocal()
    try:
        account_no = account_no.strip()
        db_account = session.query(Account).filter(Account.account_no == account_no).first()

        if not db_account:
            return {'status': "Error", "message": "Target account no does not exist."}

        session.delete(db_account)
        session.commit()
        return {'status': "Success", "message": "Account fully purged from database tables."}
    except Exception as e:
        session.rollback()
        return {'status': "Error", "message": str(e)}
    finally:
        session.close()

def get_account(account_no: str):
    session = SessionLocal()
    try:
        db_account = session.query(Account).filter(Account.account_no == str(account_no).strip()).first()
        return db_account
    finally:
        session.close()

def update_account(account_no: str, updated_data: dict):
    session = SessionLocal()
    try:
        account_no = account_no.strip()
        db_account = session.query(Account).filter(Account.account_no == account_no).first()

        if not db_account:
            return {"status": 'Error', "message": "Account no not found"}

        updated=False
        for key, value in updated_data.items():
            if hasattr(db_account, key) and value is not None:
                setattr(db_account, key, value)
                updated=True

        if not updated:
            return {"status": "Error", "message": "No valid fields were provided for update."}

        session.commit()
        session.refresh(db_account)
        return db_account
    except Exception as e:
        session.rollback()
        return {'status': "Error", "message": str(e)}
    finally:
        session.close()

def create_account_no() -> str:
    session = SessionLocal()
    try:
        while True:
            random_no = "".join([str(random.randint(0, 9)) for _ in range(9)])

            exists = session.query(Account).filter(Account.account_no == random_no).first()

            if not exists:
                return str(random_no)
    finally:
        session.close()