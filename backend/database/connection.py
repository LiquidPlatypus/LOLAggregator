import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

engine = create_engine(CONNECTION_STRING)
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass