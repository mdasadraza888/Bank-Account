from sqlalchemy import create_engine, insert, update, delete, select
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://postgres:asad888@127.0.0.1:5432/Bank Account")

Session = sessionmaker(bind=engine)
session = Session()

Account = Session
def insert_func():
    insert_query = insert()