import pytest

from dotenv import load_dotenv
from sqlalchemy import create_mock_engine
from sqlalchemy import create_engine

from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

from sqlalchemy  import String

from sqlalchemy.orm  import Mapped 
from sqlalchemy.orm  import mapped_column

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import IdentifierError


Model = declarative_base()

class User(Model):
	__tablename__ = "user"
	id: Mapped[int] = mapped_column(primary_key = True, index = True, nullable=False, unique=True)
	name: Mapped[str] = mapped_column(String(20), insert_default="")
	email: Mapped[str] = mapped_column(String, unique=True)
	username: Mapped[str] = mapped_column(String(20), unique=True)
	password: Mapped[str] = mapped_column(String)


	def __repr__(self):
		return f"User(id={self.id}, name={self.name}, email={self.email}, username={self.username})"


class TestUserDB:

	@classmethod
	def setup_class(cls):
		engine = create_engine("sqlite:///:memory:")

		Model.metadata.drop_all(engine)
		Model.metadata.create_all(engine)

		cls.db = Session(engine)

		user = User(
			name = 'prueba',
			email = 'prueba19.@gmail.com',
			username = 'prueba19',
			password = '12345'
		)

		cls.user = user

	def test_valid_create_user(self):
		new_user = self.user
		self.db.add(new_user)
		self.db.commit()
		self.db.refresh(new_user)

		assert new_user.id == 1
		assert new_user.name == "prueba"

	
	@pytest.mark.xfail(reason = "Datos invalidos", raises=IntegrityError)
	def test_invalid_create_user(self):
		""" """
		user = User(name="prueba", email="prueba19@gmail.com")
		self.db.add(user)

		try:
			self.db.commit()
		except IntegrityError as e:
			self.db.rollback()


	@pytest.mark.xfail(reason = "Email existente", raises=IntegrityError)
	def test_invalid_email_duplicate(self):
		user2 = User(
			name = 'prueba',
			email = 'prueba19.@gmail.com',
			username = 'prueba192',
			password = '12345'
		)

		self.db.add_all([self.user, user2])

		try:	
			self.db.commit()
		except IntegrityError as e:
			self.db.rollback()
		
	@pytest.mark.xfail(reason = "Username existente", raises=IntegrityError)
	def test_invalid_username_duplicate(self):
		user2 = User(
			name = 'prueba',
			email = 'prueba192.@gmail.com',
			username = 'prueba19',
			password = '12345'
		)

		self.db.add_all([self.user, user2])
		
		try:
			self.db.commit()
		except IntegrityError as e:
			self.db.rollback()

	@classmethod
	def teardown_class(cls):
		cls.db.close()

