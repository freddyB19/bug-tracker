import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DB_URL = os.getenv('DB_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM_JWT = os.getenv('ALGORITHM_JWT')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv('ACCESS_TOKEN_EXPIRE_HOURS'))
REFRESH_TOKEN_EXPIRE_HOURS = int(os.getenv('REFRESH_TOKEN_EXPIRE_HOURS'))


engine = create_engine(
	DB_URL
)

session = sessionmaker(autoflush=False, bind=engine)

def get_db():
	db = session()
	try:
		yield db
	finally:
		db.close()


class Model(DeclarativeBase):
	pass

