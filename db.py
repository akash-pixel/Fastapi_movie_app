from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from db_credentials import server, username, password, database
engine = create_engine( f"mysql+pymysql://{username}:{password}@{server}:3306/{database}", future=True )

Base = declarative_base()

SessionLocal = sessionmaker()