from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine( "mysql+pymysql://root:root@127.0.0.1:3306/MOVIE", future=True )

Base = declarative_base()

SessionLocal = sessionmaker()