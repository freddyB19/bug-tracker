from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

DB_URL = "sqlite:///./bug_tracker.db"

engine = create_engine(
	DB_URL
)

session = sessionmaker(autoflush=False, bind=engine)

def ge_db():
	db = session()
	try:
		yield db
	finally:
		db.close()


class Model(DeclarativeBase):
	pass

