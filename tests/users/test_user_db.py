import pytest

from sqlalchemy.exc import IntegrityError

from tests import ENGINE
from tests import SESSION

from apps import Model
from apps.users.models import User

class TestUserDB:

	def setup_method(self):
		Model.metadata.drop_all(ENGINE)
		Model.metadata.create_all(ENGINE)

		self.db = SESSION

		user = User(
			name = 'prueba',
			email = 'prueba19@gmail.com',
			username = 'prueba19',
			password = '12345'
		)

		self.user = user

	def test_valid_create_user(self):
		""" Validar que se cree un nuevo usuario """
		new_user = self.user
		self.db.add(new_user)
		self.db.commit()
		self.db.refresh(new_user)

		assert new_user.id == 1
		assert new_user.name == "prueba"

	
	@pytest.mark.xfail(reason = "Datos incompletos", raises=IntegrityError)
	def test_invalid_create_user(self):
		""" 
			Validar que no se cree un usuario con datos incompletos
		"""
		user = User(name="prueba", email="prueba19@gmail.com")
		self.db.add(user)
		self.db.commit()


	@pytest.mark.xfail(reason = "Email existente", raises=IntegrityError)
	def test_invalid_email_duplicate(self):
		"""
			Validar que no se cree un nuevo usuario con un 'email'
			ya registrado
		"""
		user2 = User(
			name = 'prueba',
			email = 'prueba19.@gmail.com',
			username = 'prueba192',
			password = '12345'
		)

		self.db.add_all([self.user, user2])
		self.db.commit()

		
	@pytest.mark.xfail(reason = "Username existente", raises=IntegrityError)
	def test_invalid_username_duplicate(self):
		"""
			Validar que no se cree un nuevo usuario con un 'username'
			ya registrado
		"""
		user2 = User(
			name = 'prueba',
			email = 'prueba192.@gmail.com',
			username = 'prueba19',
			password = '12345'
		)

		self.db.add_all([self.user, user2])
		self.db.commit()


	def teardown_method(self):
		self.db.rollback()
		self.db.close()

