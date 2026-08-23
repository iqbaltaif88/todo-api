from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQL_DATABASE_URL = 'mysql+pymysql://root:4321@127.0.0.1:3306/todoapplicationdatabase'
# SQL_DATABASE_URL = 'postgresql://postgres:4321@localhost/todoAplicationDatabase'
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres.btjgyygzcetvmyjoprws:XUFORIGEUtLuiNDY@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# engine = create_engine(SQL_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base() 
