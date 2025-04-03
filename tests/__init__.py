import os
import sys
import importlib

from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "apps"))

ENGINE = create_engine(
	"sqlite://", 
	poolclass=StaticPool, 
	connect_args={"check_same_thread": False}
)

SESSION = Session(ENGINE)

def get_db():
	try:
		yield SESSION
	finally:
		SESSION.close()

# command: pytest -import-mode=importlib -v {file_or_directory}