from sqlalchemy import create_engine, insert, update, delete, select, MetaData, Table
from sqlalchemy.orm import sessionmaker
from db_models import Base, Account, SavingAccount, CheckingAccount, BusinessAccount

engine = create_engine("postgresql://postgres:asad888@127.0.0.1:5432/Bank Account")

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def insert_func(account_no, account_holder, account_balance, account_pin, account_type):
    session = SessionLocal()
    try:
        new_account = Account(
            account_no = int(account_no),
            account_holder = account_holder,
            account_balance = float(account_balance),
            account_pin = account_pin,
            account_type = account_type
        )

        session.add(new_account)
        session.commit()
        session.refresh(new_account)
        return f"Your {account_type} has been created with ID: {new_account.account_id}"
    except Exception as e:
        session.rollback()
        return f"Database Error: {str(e)}"
    finally:
        session.close()


print(insert_func('136632788', "Saif", 52500.00, '1233', 'checking'))