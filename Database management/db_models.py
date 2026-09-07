from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import insert, update, delete, select

Base = declarative_base()

engine = create_engine("postgresql://postgres:asad888@127.0.0.1:5432/Bank Account")

class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True)
    account_no = Column(Integer, unique=True, nullable=False)
    account_holder = Column(String(50), nullable=False)
    account_balance = Column(Float)
    account_pin = Column(String(4), nullable=False)

    account_type = Column(String(20))
    __mapper_args__ = {
        "polymorphic_on": account_type,
        "polymorphic_identity": "generic_account"
    }

class SavingAccount(Account):
    __tablename__ = "saving_account"
    saving_id = Column(Integer, ForeignKey("account.account_id"), primary_key=True)
    account_interest = Column(Float, nullable=True, default=0.04)
    max_monthly_withdrawals = Column(Integer, default=6)

    __mapper_args__ = {
        "polymorphic_identity": "savings"
    }

class CheckingAccount(Account):
    __tablename__ = "checking_account"
    checking_id = Column(Integer, ForeignKey("account.account_id"), primary_key=True)
    overdraft_value = Column(Float, default=500.00)

    __mapper_args__ = {
        "polymorphic_identity": "checking"
    }

class BusinessAccount(Account):
    __tablename__ = "business_account"
    business_id = Column(Integer, ForeignKey("account.account_id"), primary_key=True)
    company_name = Column(String(20), nullable=False)
    transaction_fee = Column(Float, default=2.50)
    daily_withdrawal_limit = Column(Float, default=50000.00)

    __mapper_args__ = {
        "polymorphic_identity": "business"
    }

# Base.metadata.create_all(engine)
